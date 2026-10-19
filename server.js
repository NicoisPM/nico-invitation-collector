/**
 * 邀请函独立全栈本地服务 (Zero-Dependency Node.js Standalone Server)
 * 无需 npm install，开箱即用 Node.js 原生模块运行：
 *   node server.js
 * 
 * 功能：
 * 1. 自动托管 8 款邀请函 H5 页面及静态资源
 * 2. 接收 H5 报名表单提交 (/api/signup)，支持跨域 (CORS) 与本地 file:// 协议
 * 3. 数据落盘存储至 ./data/signups.json
 * 4. 提供可视化管理后台 http://localhost:3000/admin
 * 5. 提供报名名单查询与一键导出带 BOM 的 Excel/CSV 表格
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

const PORT = process.env.PORT || 3000;
const DATA_DIR = path.join(__dirname, 'data');
const DB_FILE = path.join(DATA_DIR, 'signups.json');
const TEMPLATES_DIR = path.join(__dirname, 'templates');

// 确保数据目录与数据库文件存在
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}
if (!fs.existsSync(DB_FILE)) {
  fs.writeFileSync(DB_FILE, JSON.stringify([], null, 2), 'utf-8');
}

// 全局异常捕获，确保服务永不挂掉
process.on('uncaughtException', (err) => {
  console.error('[进程守护] 捕获未处理异常:', err.message);
});
process.on('unhandledRejection', (reason) => {
  console.error('[进程守护] 捕获未处理 Promise 拒绝:', reason);
});

// 模板路由映射表
const ROUTE_MAP = {
  '/': 'nico-invitation-red-party-envelope.html',
  '/red': 'nico-invitation-red-party.html',
  '/red-envelope': 'nico-invitation-red-party-envelope.html',
  '/green': 'nico-invitation-green-eco.html',
  '/green-envelope': 'nico-invitation-green-eco-envelope.html',
  '/hk': 'nico-invitation-hk-skyline.html',
  '/hk-envelope': 'nico-invitation-hk-skyline-envelope.html',
  '/default': 'nico-invitation-framework.html',
  '/default-envelope': 'nico-invitation-envelope.html',
  '/gz': 'guangzhou-forum.html',
  '/admin': 'admin.html',
  '/themes': 'design-gallery.html',
};

// 旧母版沿用原有分类；新主题及事件保留自身标识，方便后台按活动筛选。
const LEGACY_SLUGS = {
  'red': 'red-party', 'red-party': 'red-party', '2026-red-party': 'red-party',
  'green': 'green-eco', 'green-eco': 'green-eco', '2026-green-eco': 'green-eco',
  'hk': 'hk-skyline', 'hk-skyline': 'hk-skyline', '2026-hk': 'hk-skyline',
  'default': 'default', 'default-slug': 'default',
};

// 读取全部报名数据
function readSignups() {
  try {
    const raw = fs.readFileSync(DB_FILE, 'utf-8');
    return JSON.parse(raw || '[]');
  } catch (e) {
    console.error('读取数据失败:', e);
    return [];
  }
}

// 写入报名数据
function saveSignups(data) {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2), 'utf-8');
    return true;
  } catch (e) {
    console.error('保存数据失败:', e);
    return false;
  }
}

// MIME 类型字典
const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.mp3': 'audio/mpeg',
  '.csv': 'text/csv; charset=utf-8',
};

// 创建 HTTP 服务
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method.toUpperCase();

  // 设置 CORS 跨域头（支持移动端内网访问或本地静态测试）
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // ========================== API 路由 ==========================
  
  // 1. 公开报名提交接口 POST /api/signup 或 /api/nico_invitations/signup
  if ((pathname === '/api/signup' || pathname === '/api/nico_invitations/signup') && method === 'POST') {
    let bodyStr = '';
    req.on('data', chunk => { bodyStr += chunk; });
    req.on('end', () => {
      try {
        const body = JSON.parse(bodyStr || '{}');
        const name = (body.name || '').trim();
        const company = (body.company || '').trim();
        const phone = (body.phone || '').trim();
        const title = (body.title || '').trim();
        const count = parseInt(body.count, 10) || 1;
        const note = (body.note || '').trim();
        const rawSlug = String(body.nico_invitation_slug || body.slug || 'default').trim().toLowerCase();
        const nico_invitation_slug = Object.prototype.hasOwnProperty.call(LEGACY_SLUGS, rawSlug)
          ? LEGACY_SLUGS[rawSlug]
          : (/^[a-z0-9_-]+$/.test(rawSlug) ? rawSlug : 'default');

        if (!name) {
          res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ code: 400, error: '姓名不能为空' }));
          return;
        }
        if (!phone || !/^1\d{10}$/.test(phone)) {
          res.writeHead(400, { 'Content-Type': 'application/json; charset=utf-8' });
          res.end(JSON.stringify({ code: 400, error: '请输入正确的11位手机号码' }));
          return;
        }

        const signups = readSignups();
        const newRecord = {
          id: Date.now(),
          name,
          company,
          title,
          phone,
          count,
          note,
          nico_invitation_slug,
          status: 'confirmed', // confirmed, pending, cancelled
          created_at: new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' }),
          ip: req.socket.remoteAddress || '',
        };

        signups.unshift(newRecord); // 最新置顶
        saveSignups(signups);

        console.log(`[新增报名] ${newRecord.name} (${newRecord.company}) 电话:${newRecord.phone}`);

        res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({
          code: 0,
          message: '报名信息已成功提交！',
          data: newRecord,
        }));
      } catch (err) {
        console.error('解析请求异常:', err.message, 'body:', bodyStr);
        res.writeHead(500, { 'Content-Type': 'application/json; charset=utf-8' });
        res.end(JSON.stringify({ code: 500, error: '服务器解析请求失败: ' + err.message }));
      }
    });
    return;
  }

  // 2. 获取报名列表 GET /api/signups
  if (pathname === '/api/signups' && method === 'GET') {
    const signups = readSignups();
    const query = parsedUrl.query;
    let list = [...signups];

    // 关键词过滤 (姓名/单位/手机号)
    if (query.keyword) {
      const kw = query.keyword.toLowerCase();
      list = list.filter(item => 
        (item.name && item.name.toLowerCase().includes(kw)) ||
        (item.company && item.company.toLowerCase().includes(kw)) ||
        (item.phone && item.phone.includes(kw))
      );
    }

    // 主题过滤
    if (query.slug) {
      list = list.filter(item => item.nico_invitation_slug === query.slug);
    }

    // 统计总览
    const stats = {
      total: signups.length,
      today: signups.filter(s => {
        const todayStr = new Date().toLocaleDateString('zh-CN', { timeZone: 'Asia/Shanghai' });
        return s.created_at && s.created_at.startsWith(todayStr);
      }).length,
      companies: new Set(signups.map(s => s.company).filter(Boolean)).size,
      headcount: signups.reduce((sum, s) => sum + (s.count || 1), 0),
    };

    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({
      code: 0,
      data: {
        list,
        stats,
      }
    }));
    return;
  }

  // 3. 导出 CSV 表格 GET /api/signups/export
  if (pathname === '/api/signups/export' && method === 'GET') {
    const signups = readSignups();
    // 写入 UTF-8 BOM (\uFEFF) 保证中文在 Excel 直开不乱码
    let csv = '\uFEFFID,姓名,单位,职务,手机号,参会人数,备注,所属模板,状态,报名时间\n';
    signups.forEach(s => {
      const row = [
        s.id,
        `"${(s.name || '').replace(/"/g, '""')}"`,
        `"${(s.company || '').replace(/"/g, '""')}"`,
        `"${(s.title || '').replace(/"/g, '""')}"`,
        `"${s.phone || ''}"`,
        s.count || 1,
        `"${(s.note || '').replace(/"/g, '""')}"`,
        `"${s.nico_invitation_slug || 'default'}"`,
        `"${s.status || 'confirmed'}"`,
        `"${s.created_at || ''}"`,
      ];
      csv += row.join(',') + '\n';
    });

    const filename = `报名名单导出_${Date.now()}.csv`;
    res.writeHead(200, {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': `attachment; filename="${encodeURIComponent(filename)}"`,
    });
    res.end(csv);
    return;
  }

  // 4. 删除报名记录 DELETE /api/signups/:id
  if (pathname.startsWith('/api/signups/') && method === 'DELETE') {
    const idStr = pathname.replace('/api/signups/', '');
    const targetId = parseInt(idStr, 10);
    let signups = readSignups();
    const initialLen = signups.length;
    signups = signups.filter(s => s.id !== targetId);

    if (signups.length === initialLen) {
      res.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(JSON.stringify({ code: 404, error: '记录不存在' }));
      return;
    }

    saveSignups(signups);
    res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
    res.end(JSON.stringify({ code: 0, message: '删除成功' }));
    return;
  }

  // ========================== 静态文件托管 ==========================

  let staticPathname;
  try {
    staticPathname = decodeURIComponent(pathname);
  } catch (err) {
    res.writeHead(400, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('请求路径编码无效');
    return;
  }
  
  let targetFile = '';
  if (ROUTE_MAP[staticPathname]) {
    targetFile = path.join(TEMPLATES_DIR, ROUTE_MAP[staticPathname]);
  } else {
    const safePath = path.normalize(staticPathname).replace(/^(\.\.[\/\\])+/, '');
    const templateCandidate = path.join(TEMPLATES_DIR, safePath);
    const rootCandidate = path.join(__dirname, safePath);
    
    // 递归检查文件或对应目录下的 index.html
    const resolveCandidate = (p) => {
      try {
        if (!fs.existsSync(p)) return null;
        const stat = fs.statSync(p);
        if (stat.isFile()) return p;
        if (stat.isDirectory()) {
          const idx = path.join(p, 'index.html');
          if (fs.existsSync(idx) && fs.statSync(idx).isFile()) return idx;
        }
      } catch (e) {}
      return null;
    };

    targetFile = resolveCandidate(rootCandidate) ||
                 resolveCandidate(templateCandidate) ||
                 templateCandidate;
  }

  fs.stat(targetFile, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(`
        <div style="font-family:sans-serif; text-align:center; padding:50px;">
          <h2>404 - 页面未找到</h2>
          <p>请求的路径 <code>${pathname}</code> 不存在。</p>
          <hr style="max-width:400px; margin:20px auto; border:none; border-top:1px solid #ddd;" />
          <p>可用入口：</p>
          <p><a href="/admin">📊 管理员后台 (/admin)</a></p>
          <p><a href="/red">🔴 红色党建直入版 (/red)</a> | <a href="/red-envelope">✉️ 红色党建信封版 (/red-envelope)</a></p>
          <p><a href="/green">🟢 绿色生态直入版 (/green)</a> | <a href="/green-envelope">✉️ 绿色生态信封版 (/green-envelope)</a></p>
          <p><a href="/hk">🌃 维港夜景直入版 (/hk)</a> | <a href="/hk-envelope">✉️ 维港夜景信封版 (/hk-envelope)</a></p>
          <p><a href="/default">📜 金调纸质直入版 (/default)</a> | <a href="/default-envelope">✉️ 金调纸质信封版 (/default-envelope)</a></p>
        </div>
      `);
      return;
    }

    const ext = path.extname(targetFile).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    const stream = fs.createReadStream(targetFile);
    stream.on('error', (streamErr) => {
      console.error('[静态流错误]', streamErr.message);
    });
    stream.pipe(res);
  });
});

server.listen(PORT, () => {
  console.log(`\n======================================================`);
  console.log(`🚀 邀请函全栈服务已就绪！(Node.js Zero-Dependency Server)`);
  console.log(`======================================================`);
  console.log(`📊 管理后台入口:   http://localhost:${PORT}/admin`);
  console.log(`🎨 邀请函主题库:   http://localhost:${PORT}/themes`);
  console.log(`🔴 红色党建直入:   http://localhost:${PORT}/red`);
  console.log(`✉️ 红色党建信封:   http://localhost:${PORT}/red-envelope`);
  console.log(`🟢 绿色生态直入:   http://localhost:${PORT}/green`);
  console.log(`✉️ 绿色生态信封:   http://localhost:${PORT}/green-envelope`);
  console.log(`🌃 维港夜景直入:   http://localhost:${PORT}/hk`);
  console.log(`✉️ 维港夜景信封:   http://localhost:${PORT}/hk-envelope`);
  console.log(`📜 金调标准直入:   http://localhost:${PORT}/default`);
  console.log(`✉️ 金调标准信封:   http://localhost:${PORT}/default-envelope`);
  console.log(`🏛️ 广州论坛专版:   http://localhost:${PORT}/gz`);
  console.log(`======================================================\n`);
});
