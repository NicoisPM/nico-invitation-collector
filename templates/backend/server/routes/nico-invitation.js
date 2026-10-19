const express = require('express');
const path = require('path');
const fs = require('fs');
const multer = require('multer');
const config = require('../config');
const adminAuth = require('../middleware/auth');

// 配置邀请函 HTML 文件上传存储
const nicoInvitationsDir = path.join(config.upload.dir, 'nico_invitations');
if (!fs.existsSync(nicoInvitationsDir)) {
  fs.mkdirSync(nicoInvitationsDir, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, nicoInvitationsDir);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname) || '.html';
    const safeName = `invite_${Date.now()}${ext}`;
    cb(null, safeName);
  },
});

const upload = multer({
  storage,
  limits: { fileSize: 20 * 1024 * 1024 },
});

/**
 * 确保默认邀请函已入库且 HTML 文件已同步至服务器目录
 */
async function ensureDefaultNicoInvitation(db) {
  try {
    const defaultFilename = 'nico_invitation_default.html';
    const destPath = path.join(nicoInvitationsDir, defaultFilename);
    const rootHtmlPath = path.resolve(__dirname, '../../../nico_invitation_default.html');
    const h5HtmlPath = path.resolve(__dirname, '../../../client-h5/public/1.html');

    // 复制最新的 nico_invitation_2026.html 到 uploads/nico_invitations/
    if (fs.existsSync(rootHtmlPath)) {
      fs.copyFileSync(rootHtmlPath, destPath);
    } else if (fs.existsSync(h5HtmlPath)) {
      fs.copyFileSync(h5HtmlPath, destPath);
    }

    const existing = await db('nico_invitations').where('slug', 'default').first();
    if (!existing) {
      await db('nico_invitations').insert({
        title: '活动邀请函',
        slug: 'default',
        file_path: `/uploads/nico_invitations/${defaultFilename}`,
        event_time: '',
        deadline: '',
        organizer: '',
        status: 'active',
        view_count: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      console.log('✅ 已自动初始化默认邀请函');
    }
  } catch (err) {
    console.error('初始化默认邀请函失败:', err.message);
  }
}

/**
 * 创建邀请函与预约管理路由
 */
function createNicoInvitationRouter(db) {
  const router = express.Router();

  // 启动时确保默认邀请函存在
  ensureDefaultNicoInvitation(db);

  // ==========================================
  // 一、公开接口：提交预约报名 (H5 邀请函表单调用)
  // POST /api/nico_invitations/signup  或  POST /api/signup
  // ==========================================
  const handlePublicSignup = async (req, res) => {
    try {
      const {
        nico_invitation_id,
        slug = 'default',
        name,
        company,
        title = '',
        phone,
        count = 1,
        note = '',
      } = req.body || {};

      if (!name || !String(name).trim()) {
        return res.status(400).json({ success: false, message: '请填写您的姓名' });
      }
      if (!company || !String(company).trim()) {
        return res.status(400).json({ success: false, message: '请填写企业名称' });
      }
      if (!phone || !/^1[3-9]\d{9}$/.test(String(phone).trim())) {
        return res.status(400).json({ success: false, message: '请填写正确的 11 位手机号码' });
      }

      // 查找关联的邀请函
      let nicoInvitation = null;
      if (nico_invitation_id) {
        nicoInvitation = await db('nico_invitations').where('id', nico_invitation_id).first();
      }
      if (!nicoInvitation && slug) {
        nicoInvitation = await db('nico_invitations').where('slug', slug).first();
      }
      if (!nicoInvitation) {
        nicoInvitation = await db('nico_invitations').orderBy('id', 'asc').first();
      }

      if (nicoInvitation && nicoInvitation.status === 'closed') {
        return res.status(400).json({
          success: false,
          message: '本期报名已截止，如需咨询请联系活动负责人',
        });
      }

      const parsedCount = Math.max(1, parseInt(count, 10) || 1);
      const clientIp =
        req.headers['x-forwarded-for']?.split(',')[0]?.trim() ||
        req.socket?.remoteAddress ||
        '';

      const now = new Date().toISOString();
      const insertData = {
        nico_invitation_id: nicoInvitation ? nicoInvitation.id : null,
        nico_invitation_title: nicoInvitation ? nicoInvitation.title : '活动邀请函',
        name: String(name).trim(),
        phone: String(phone).trim(),
        company: String(company).trim(),
        title: String(title || '').trim(),
        count: parsedCount,
        note: String(note || '').trim(),
        status: 'pending',
        admin_remark: '',
        ip: clientIp,
        created_at: now,
        updated_at: now,
      };

      const [id] = await db('nico_invitation_signups').insert(insertData);
      const record = await db('nico_invitation_signups').where('id', id).first();

      res.status(201).json({
        success: true,
        data: record,
        message: '预约报名提交成功！我们的教务老师将尽快与您联系。',
      });
    } catch (err) {
      console.error('提交预约报名失败:', err.message);
      res.status(500).json({
        success: false,
        message: '提交预约失败，请稍后重试或直接拨打老师电话',
      });
    }
  };

  router.post('/signup', handlePublicSignup);

  // ==========================================
  // 二、后台管理：预约报名信息管理 (/api/nico_invitations/signups/*)
  // ==========================================

  /**
   * 获取预约报名列表与统计
   * GET /api/nico_invitations/signups
   */
  router.get('/signups', adminAuth, async (req, res) => {
    try {
      const { page = 1, pageSize = 15, keyword, status, nico_invitation_id } = req.query;

      let query = db('nico_invitation_signups');

      if (nico_invitation_id) {
        query = query.where('nico_invitation_id', nico_invitation_id);
      }
      if (status) {
        query = query.where('status', status);
      }
      if (keyword && String(keyword).trim()) {
        const kw = `%${String(keyword).trim()}%`;
        query = query.where(function () {
          this.where('name', 'like', kw)
            .orWhere('phone', 'like', kw)
            .orWhere('company', 'like', kw)
            .orWhere('title', 'like', kw)
            .orWhere('note', 'like', kw);
        });
      }

      const totalQuery = query.clone();
      const { count: total } = await totalQuery.count('id as count').first();

      const list = await query
        .orderBy('created_at', 'desc')
        .limit(parseInt(pageSize, 10))
        .offset((parseInt(page, 10) - 1) * parseInt(pageSize, 10));

      // 全局统计数据
      let statsQuery = db('nico_invitation_signups');
      if (nico_invitation_id) {
        statsQuery = statsQuery.where('nico_invitation_id', nico_invitation_id);
      }
      const statsRow = await statsQuery
        .select(
          db.raw('COUNT(*) as total_orders'),
          db.raw("SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count"),
          db.raw("SUM(CASE WHEN status = 'contacted' THEN 1 ELSE 0 END) as contacted_count"),
          db.raw("SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_count"),
          db.raw("SUM(CASE WHEN status != 'cancelled' THEN COALESCE(count, 1) ELSE 0 END) as total_attendees")
        )
        .first();

      res.json({
        success: true,
        data: {
          list,
          total: Number(total || 0),
          page: parseInt(page, 10),
          pageSize: parseInt(pageSize, 10),
          stats: {
            total_orders: Number(statsRow?.total_orders || 0),
            pending_count: Number(statsRow?.pending_count || 0),
            contacted_count: Number(statsRow?.contacted_count || 0),
            confirmed_count: Number(statsRow?.confirmed_count || 0),
            total_attendees: Number(statsRow?.total_attendees || 0),
          },
        },
      });
    } catch (err) {
      console.error('获取预约列表失败:', err.message);
      res.status(500).json({ success: false, message: '获取预约列表失败' });
    }
  });

  /**
   * 导出预约报名列表为 CSV (Excel 可直接打开)
   * GET /api/nico_invitations/signups/export
   */
  router.get('/signups/export', adminAuth, async (req, res) => {
    try {
      const { keyword, status, nico_invitation_id } = req.query;
      let query = db('nico_invitation_signups');

      if (nico_invitation_id) query = query.where('nico_invitation_id', nico_invitation_id);
      if (status) query = query.where('status', status);
      if (keyword && String(keyword).trim()) {
        const kw = `%${String(keyword).trim()}%`;
        query = query.where(function () {
          this.where('name', 'like', kw)
            .orWhere('phone', 'like', kw)
            .orWhere('company', 'like', kw)
            .orWhere('title', 'like', kw);
        });
      }

      const rows = await query.orderBy('created_at', 'desc');
      const statusMap = {
        pending: '待联系',
        contacted: '已联系',
        confirmed: '已确认参会',
        cancelled: '已取消',
      };

      const escapeCsv = (val) => {
        const str = String(val ?? '').replace(/"/g, '""');
        return `"${str}"`;
      };

      const headers = [
        '序号',
        '所属邀请函',
        '姓名',
        '手机号',
        '企业名称',
        '职务',
        '报名人数',
        '关注议题/备注',
        '跟进状态',
        '教务跟进备注',
        '提交时间',
      ];

      const lines = [headers.map(escapeCsv).join(',')];
      rows.forEach((r, idx) => {
        lines.push(
          [
            idx + 1,
            r.nico_invitation_title || '',
            r.name || '',
            r.phone || '',
            r.company || '',
            r.title || '',
            r.count || 1,
            r.note || '',
            statusMap[r.status] || r.status,
            r.admin_remark || '',
            r.created_at || '',
          ]
            .map(escapeCsv)
            .join(',')
        );
      });

      const csvContent = '\uFEFF' + lines.join('\r\n');
      res.setHeader('Content-Type', 'text/csv; charset=utf-8');
      res.setHeader(
        'Content-Disposition',
        `attachment; filename="nico_invitation_signups_${Date.now()}.csv"`
      );
      res.send(csvContent);
    } catch (err) {
      console.error('导出预约信息失败:', err.message);
      res.status(500).json({ success: false, message: '导出失败' });
    }
  });

  /**
   * 后台手动新增或修改预约记录
   * PUT /api/nico_invitations/signups/:id
   */
  router.put('/signups/:id', adminAuth, async (req, res) => {
    try {
      const { id } = req.params;
      const existing = await db('nico_invitation_signups').where('id', id).first();
      if (!existing) {
        return res.status(404).json({ success: false, message: '预约记录不存在' });
      }

      const { name, phone, company, title, count, note, status, admin_remark } = req.body;
      const updateData = { updated_at: new Date().toISOString() };

      if (name !== undefined) updateData.name = String(name).trim();
      if (phone !== undefined) updateData.phone = String(phone).trim();
      if (company !== undefined) updateData.company = String(company).trim();
      if (title !== undefined) updateData.title = String(title).trim();
      if (count !== undefined) updateData.count = Math.max(1, parseInt(count, 10) || 1);
      if (note !== undefined) updateData.note = String(note).trim();
      if (status !== undefined) updateData.status = status;
      if (admin_remark !== undefined) updateData.admin_remark = String(admin_remark).trim();

      await db('nico_invitation_signups').where('id', id).update(updateData);
      const updated = await db('nico_invitation_signups').where('id', id).first();

      res.json({
        success: true,
        data: updated,
        message: '预约信息已更新',
      });
    } catch (err) {
      console.error('更新预约信息失败:', err.message);
      res.status(500).json({ success: false, message: '更新预约信息失败' });
    }
  });

  /**
   * 删除预约记录
   * DELETE /api/nico_invitations/signups/:id
   */
  router.delete('/signups/:id', adminAuth, async (req, res) => {
    try {
      const { id } = req.params;
      const deleted = await db('nico_invitation_signups').where('id', id).del();
      if (!deleted) {
        return res.status(404).json({ success: false, message: '记录不存在' });
      }
      res.json({ success: true, message: '预约记录已删除' });
    } catch (err) {
      console.error('删除预约信息失败:', err.message);
      res.status(500).json({ success: false, message: '删除失败' });
    }
  });

  // ==========================================
  // 三、后台管理：邀请函管理 (/api/nico_invitations)
  // ==========================================

  /**
   * 获取邀请函列表（含各自预约人数统计）
   * GET /api/nico_invitations
   */
  router.get('/', adminAuth, async (req, res) => {
    try {
      const { keyword, status } = req.query;
      let query = db('nico_invitations');

      if (status) {
        query = query.where('status', status);
      }
      if (keyword && String(keyword).trim()) {
        const kw = `%${String(keyword).trim()}%`;
        query = query.where(function () {
          this.where('title', 'like', kw)
            .orWhere('slug', 'like', kw)
            .orWhere('organizer', 'like', kw);
        });
      }

      const list = await query.orderBy('id', 'desc');

      const enriched = await Promise.all(
        list.map(async (inv) => {
          const stats = await db('nico_invitation_signups')
            .where('nico_invitation_id', inv.id)
            .select(
              db.raw('COUNT(*) as signup_count'),
              db.raw("SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count"),
              db.raw("SUM(CASE WHEN status = 'confirmed' THEN 1 ELSE 0 END) as confirmed_count"),
              db.raw("SUM(CASE WHEN status != 'cancelled' THEN COALESCE(count, 1) ELSE 0 END) as attendee_count")
            )
            .first();

          return {
            ...inv,
            signup_count: Number(stats?.signup_count || 0),
            pending_count: Number(stats?.pending_count || 0),
            confirmed_count: Number(stats?.confirmed_count || 0),
            attendee_count: Number(stats?.attendee_count || 0),
          };
        })
      );

      res.json({
        success: true,
        data: {
          list: enriched,
          total: enriched.length,
        },
      });
    } catch (err) {
      console.error('获取邀请函列表失败:', err.message);
      res.status(500).json({ success: false, message: '获取邀请函列表失败' });
    }
  });

  /**
   * 获取单个邀请函详情及 HTML 源码内容
   * GET /api/nico_invitations/:id
   */
  router.get('/:id', adminAuth, async (req, res) => {
    try {
      const inv = await db('nico_invitations').where('id', req.params.id).first();
      if (!inv) {
        return res.status(404).json({ success: false, message: '邀请函不存在' });
      }

      let htmlContent = '';
      const diskPath = path.join(config.upload.dir, inv.file_path.replace(/^\/uploads[\\/]?/, ''));
      if (fs.existsSync(diskPath)) {
        htmlContent = fs.readFileSync(diskPath, 'utf8');
      }

      res.json({
        success: true,
        data: {
          ...inv,
          content: htmlContent,
        },
      });
    } catch (err) {
      console.error('获取邀请函详情失败:', err.message);
      res.status(500).json({ success: false, message: '获取邀请函详情失败' });
    }
  });

  /**
   * 新增/上传邀请函
   * POST /api/nico_invitations
   */
  router.post('/', adminAuth, upload.single('file'), async (req, res) => {
    try {
      const {
        title,
        slug,
        event_time = '',
        deadline = '',
        organizer = '',
        status = 'active',
        content = '',
      } = req.body;

      if (!title || !String(title).trim()) {
        return res.status(400).json({ success: false, message: '请填写邀请函标题' });
      }

      const finalSlug = (slug && String(slug).trim()) || `invite-${Date.now()}`;
      const existingSlug = await db('nico_invitations').where('slug', finalSlug).first();
      if (existingSlug) {
        return res.status(400).json({ success: false, message: '短路径标识 (slug) 已存在，请更换' });
      }

      let filePath = '';
      if (req.file) {
        filePath = `/uploads/nico_invitations/${req.file.filename}`;
      } else if (content && String(content).trim()) {
        const filename = `invite_${finalSlug}_${Date.now()}.html`;
        fs.writeFileSync(path.join(nicoInvitationsDir, filename), content, 'utf8');
        filePath = `/uploads/nico_invitations/${filename}`;
      } else {
        return res.status(400).json({ success: false, message: '请上传 HTML 文件或填写 HTML 内容' });
      }

      const now = new Date().toISOString();
      const [id] = await db('nico_invitations').insert({
        title: String(title).trim(),
        slug: finalSlug,
        file_path: filePath,
        event_time: String(event_time).trim(),
        deadline: String(deadline).trim(),
        organizer: String(organizer).trim(),
        status,
        view_count: 0,
        created_at: now,
        updated_at: now,
      });

      const created = await db('nico_invitations').where('id', id).first();
      res.status(201).json({
        success: true,
        data: created,
        message: '邀请函创建成功',
      });
    } catch (err) {
      console.error('创建邀请函失败:', err.message);
      res.status(500).json({ success: false, message: '创建邀请函失败: ' + err.message });
    }
  });

  /**
   * 更新邀请函信息或重新上传 HTML 文件
   * PUT /api/nico_invitations/:id
   */
  router.put('/:id', adminAuth, upload.single('file'), async (req, res) => {
    try {
      const { id } = req.params;
      const inv = await db('nico_invitations').where('id', id).first();
      if (!inv) {
        return res.status(404).json({ success: false, message: '邀请函不存在' });
      }

      const { title, slug, event_time, deadline, organizer, status, content } = req.body;
      const updateData = { updated_at: new Date().toISOString() };

      if (title !== undefined) updateData.title = String(title).trim();
      if (slug !== undefined && String(slug).trim() !== inv.slug) {
        const dup = await db('nico_invitations')
          .where('slug', String(slug).trim())
          .whereNot('id', id)
          .first();
        if (dup) {
          return res.status(400).json({ success: false, message: '短路径标识已被占用' });
        }
        updateData.slug = String(slug).trim();
      }
      if (event_time !== undefined) updateData.event_time = String(event_time).trim();
      if (deadline !== undefined) updateData.deadline = String(deadline).trim();
      if (organizer !== undefined) updateData.organizer = String(organizer).trim();
      if (status !== undefined) updateData.status = status;

      // 如果上传了新文件或提交了新 HTML 源码
      const diskPath = path.join(config.upload.dir, inv.file_path.replace(/^\/uploads[\\/]?/, ''));
      if (req.file) {
        const uploadedContent = fs.readFileSync(req.file.path, 'utf8');
        fs.writeFileSync(diskPath, uploadedContent, 'utf8');
        if (req.file.path !== diskPath && fs.existsSync(req.file.path)) {
          fs.unlinkSync(req.file.path);
        }
      } else if (content !== undefined && String(content).trim()) {
        fs.writeFileSync(diskPath, content, 'utf8');
      }

      // 若是默认邀请函，同步更新根目录与 H5 静态目录（按需保留/删除）
      if ((req.file || (content !== undefined && String(content).trim())) && (inv.slug === 'default' || Number(id) === 1)) {
        const latestHtml = fs.readFileSync(diskPath, 'utf8');
        const rootHtmlPath = path.resolve(__dirname, '../../../nico_invitation_default.html');
        const h5HtmlPath = path.resolve(__dirname, '../../../client-h5/public/1.html');
        try {
          fs.writeFileSync(rootHtmlPath, latestHtml, 'utf8');
          if (fs.existsSync(path.dirname(h5HtmlPath))) {
            fs.writeFileSync(h5HtmlPath, latestHtml, 'utf8');
          }
        } catch (syncErr) {
          console.warn('同步邀请函文件警告:', syncErr.message);
        }
      }

      await db('nico_invitations').where('id', id).update(updateData);
      const updated = await db('nico_invitations').where('id', id).first();

      res.json({
        success: true,
        data: updated,
        message: '邀请函已更新',
      });
    } catch (err) {
      console.error('更新邀请函失败:', err.message);
      res.status(500).json({ success: false, message: '更新邀请函失败' });
    }
  });

  /**
   * 删除邀请函
   * DELETE /api/nico_invitations/:id
   */
  router.delete('/:id', adminAuth, async (req, res) => {
    try {
      const { id } = req.params;
      const inv = await db('nico_invitations').where('id', id).first();
      if (!inv) {
        return res.status(404).json({ success: false, message: '邀请函不存在' });
      }
      await db('nico_invitations').where('id', id).del();
      res.json({ success: true, message: '邀请函已删除' });
    } catch (err) {
      console.error('删除邀请函失败:', err.message);
      res.status(500).json({ success: false, message: '删除邀请函失败' });
    }
  });

  return { router, handlePublicSignup };
}

module.exports = createNicoInvitationRouter;
