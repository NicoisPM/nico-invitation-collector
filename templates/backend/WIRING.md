# 接线说明（把模块接进一个已有的 Express + Vue 管理端项目）

本模块刻意做成**可插拔**：不依赖任何具体业务，接进即可用。

---

## 一、后端（server，Express + Knex + SQLite/MySQL 皆可）

### 1. 放置文件
| 模板文件 | 放到项目 |
|---|---|
| `server/routes/nico-invitation.js` | `<server>/src/routes/nico-invitation.js` |
| `server/db/migrations/20260101000000_create_nico_invitations_and_signups.js` | `<server>/src/db/migrations/` |

### 2. 依赖（须已存在）
- `express`、`multer`（上传邀请函 HTML）、`knex`（注入的 `db` 实例）
- `../middleware/auth`：一个**管理员鉴权中间件**（校验 JWT/会话），原型可先用 `(req,res,next)=>next()`
- `../config`：需暴露 `upload.dir`（上传根目录的绝对路径）

### 3. 在 `app.js` 注册
```js
const createNicoInvitationRouter = require('./routes/nico-invitation');
// ...
const { router: nicoInvitationRouter, handlePublicSignup } = createNicoInvitationRouter(db);
app.use('/api/nico_invitations', nicoInvitationRouter);   // 后台管理 + 公开报名(signup)
app.post('/api/signup', handlePublicSignup);     // H5 表单提交的短别名
```

### 4. 托管邀请函页面（H5 访问入口）
把 H5 邀请函放到 `config.upload.dir` 下，并让服务端按 slug 返回：
```js
app.get('/invite/:slug', async (req, res) => {
  const inv = await db('nico_invitations').where('slug', req.params.slug).first()
           || await db('nico_invitations').orderBy('id').first();
  if (!inv) return res.status(404).send('邀请函不存在');
  await db('nico_invitations').where('id', inv.id).increment('view_count', 1);
  const diskPath = path.resolve(config.upload.dir, inv.file_path.replace(/^\/uploads[\/\\]?/, ''));
  res.sendFile(diskPath);
});
app.use('/uploads', express.static(config.upload.dir));  // 静态资源（含邀请函 HTML、二维码文档页、bgm.mp3）
```

### 5. 环境变量
```
PORT=3000
DB_PATH=./data/app.db
UPLOAD_DIR=./uploads
```

### 6. 接口一览
| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/signup` 或 `/api/nico_invitations/signup` | **公开**：报名提交（name/company 必填，phone 需 11 位手机号） |
| GET | `/api/nico_invitations/signups` | 报名列表 + 统计（分页、关键词、状态、nico_invitation_id） |
| GET | `/api/nico_invitations/signups/export` | 导出 CSV（带 BOM，Excel 直开） |
| PUT | `/api/nico_invitations/signups/:id` | 编辑/跟进（状态、备注、基本信息） |
| DELETE | `/api/nico_invitations/signups/:id` | 删除报名记录 |
| GET | `/api/nico_invitations` | 邀请函列表（含各自报名统计） |
| GET | `/api/nico_invitations/:id` | 邀请函详情（含 HTML 源码） |
| POST | `/api/nico_invitations` | 新增/上传邀请函（multipart：file 或 content） |
| PUT | `/api/nico_invitations/:id` | 更新邀请函（可重传 HTML） |
| DELETE | `/api/nico_invitations/:id` | 删除邀请函 |

---

## 二、管理端（Vue3 + Element Plus）

### 1. 放置文件
| 模板文件 | 放到项目 |
|---|---|
| `admin/api/nico-invitation.js` | `src/api/nico-invitation.js` |
| `admin/views/NicoInvitationList.vue` | `src/views/nico-invitation/NicoInvitationList.vue` |
| `admin/views/SignupList.vue` | `src/views/nico-invitation/SignupList.vue` |

### 2. 依赖
- `element-plus`、`@element-plus/icons-vue`
- `src/api/index.js`：一个 axios 实例（`request`），响应拦截器统一解包 `{ success, data, message }`

### 3. 注册路由（`src/router/index.js`，放进已登录的 Layout 子路由）
```js
{ path: 'nico_invitations', name: 'NicoInvitationList',
  component: () => import('../views/nico-invitation/NicoInvitationList.vue'), meta: { title: '邀请函管理' } },
{ path: 'signups', name: 'SignupList',
  component: () => import('../views/nico-invitation/SignupList.vue'), meta: { title: '报名信息管理' } },
```

### 4. 侧边栏菜单（`src/views/Layout.vue`）
```html
<el-menu-item index="/nico_invitations">邀请函管理</el-menu-item>
<el-menu-item index="/signups">报名信息管理</el-menu-item>
```

### 5. 需要你补齐的两处
- `NicoInvitationList.vue` 顶部常量 `H5_INVITE_SLUG`：若你的 H5 走独立地址（如 `/1.html`），填上对应 slug 才会显示该快捷入口；不需要则留空。
- `SignupList.vue` 里"所属邀请函"下拉依赖 `/api/nico_invitations`，确保后端已注册。

---

## 三、可插拔性说明
- 本模块只用两张表：`nico_invitations`、`nico_invitation_signups`，可独立迁移。
- 不写死任何业务字段：报名表字段（姓名/企业/职务/电话/人数/留言）如需增删，改
  `migration` 表结构 + `routes/nico-invitation.js` 的 `insertData`/校验 + `SignupList.vue` 表单即可。
- 与"合同签署"等其它模块**无耦合**，可单独使用。
