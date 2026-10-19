<template>
  <div class="nico-invitation-list-page">
    <!-- 顶部搜索与操作栏 -->
    <div class="page-card">
      <div class="table-toolbar">
        <div class="table-toolbar-left">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索邀请函标题 / 标识 / 主承办单位"
            clearable
            style="width: 280px"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-select
            v-model="filters.status"
            placeholder="状态筛选"
            clearable
            style="width: 140px"
            @change="handleSearch"
          >
            <el-option label="进行中" value="active" />
            <el-option label="已截止" value="closed" />
          </el-select>

          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </div>

        <div>
          <el-button type="primary" @click="openEditDialog()">
            <el-icon><Upload /></el-icon>
            上传 / 新增邀请函
          </el-button>
        </div>
      </div>

      <!-- 邀请函列表表格 -->
      <el-table :data="nicoInvitationList" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="65" />

        <el-table-column label="邀请函名称与主办信息" min-width="240">
          <template #default="{ row }">
            <div style="font-weight: 600; color: #303133; font-size: 14px">{{ row.title }}</div>
            <div style="font-size: 12px; color: #909399; margin-top: 4px">
              {{ row.organizer || '-' }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="开课与截止时间" width="180">
          <template #default="{ row }">
            <div style="font-size: 13px; color: #303133">
              <span style="color: #909399">开课：</span>{{ row.event_time || '-' }}
            </div>
            <div style="font-size: 12px; color: #f56c6c; margin-top: 3px">
              <span>截止：</span>{{ row.deadline || '-' }}
            </div>
          </template>
        </el-table-column>

        <el-table-column label="服务器在线访问地址" min-width="250">
          <template #default="{ row }">
            <div class="link-row">
              <el-tag size="small" type="info" effect="plain">服务器直链</el-tag>
              <a :href="getServerInviteUrl(row)" target="_blank" class="invite-link">
                {{ getServerInviteUrl(row) }}
              </a>
              <el-button link type="primary" size="small" @click="copyText(getServerInviteUrl(row))">
                复制
              </el-button>
            </div>
            <div class="link-row" style="margin-top: 4px" v-if="H5_INVITE_SLUG && row.slug === H5_INVITE_SLUG">
              <el-tag size="small" type="warning" effect="plain">H5端地址</el-tag>
              <a :href="getH5DirectUrl()" target="_blank" class="invite-link">
                {{ getH5DirectUrl() }}
              </a>
              <el-button link type="primary" size="small" @click="copyText(getH5DirectUrl())">
                复制
              </el-button>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="浏览 / 预约统计" width="165" align="center">
          <template #default="{ row }">
            <div style="display: flex; justify-content: center; gap: 6px; flex-wrap: wrap">
              <el-tag size="small" type="info">浏览 {{ row.view_count || 0 }}</el-tag>
              <el-tag
                size="small"
                type="primary"
                style="cursor: pointer"
                @click="goToSignups(row)"
              >
                预约 {{ row.signup_count || 0 }} 单 ({{ row.attendee_count || 0 }}人)
              </el-tag>
            </div>
            <div v-if="row.pending_count > 0" style="margin-top: 4px">
              <el-tag
                size="small"
                type="danger"
                effect="light"
                style="cursor: pointer"
                @click="goToSignups(row)"
              >
                {{ row.pending_count }} 单待联系
              </el-tag>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="报名状态" width="105" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.status"
              active-value="active"
              inactive-value="closed"
              active-text="进行中"
              inactive-text="已截止"
              inline-prompt
              @change="(val) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" @click="goToSignups(row)">
              <el-icon><List /></el-icon>
              预约名单
            </el-button>
            <el-button link type="warning" @click="openEditDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑/上传
            </el-button>
            <el-button
              v-if="row.id !== 1"
              link
              type="danger"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 手机端实时预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      :title="`邀请函在线预览 - ${previewRow?.title || ''}`"
      width="470px"
      top="4vh"
      destroy-on-close
    >
      <div class="phone-preview-wrap">
        <div class="phone-Preview-toolbar">
          <el-button size="small" type="primary" plain @click="copyText(getServerInviteUrl(previewRow))">
            复制分享链接
          </el-button>
          <el-button size="small" @click="openNewTab(getServerInviteUrl(previewRow))">
            新窗口全屏打开
          </el-button>
        </div>
        <div class="phone-frame">
          <iframe
            v-if="previewUrl"
            :src="previewUrl"
            class="phone-iframe"
            frameborder="0"
          ></iframe>
        </div>
      </div>
    </el-dialog>

    <!-- 新增 / 编辑 / 上传更新邀请函弹窗 -->
    <el-dialog
      v-model="editVisible"
      :title="editForm.id ? '编辑 / 更新邀请函页面' : '上传 / 新增邀请函'"
      width="720px"
      top="5vh"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="110px"
      >
        <el-form-item label="邀请函标题" prop="title">
          <el-input v-model="editForm.title" placeholder="例如：某某活动邀请函" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="访问标识(slug)" prop="slug">
              <el-input v-model="editForm.slug" placeholder="如：my-event" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报名状态">
              <el-radio-group v-model="editForm.status">
                <el-radio value="active">进行中</el-radio>
                <el-radio value="closed">已截止</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="开课时间">
              <el-input v-model="editForm.event_time" placeholder="如：2026.12.01 - 12.04" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报名截止">
              <el-input v-model="editForm.deadline" placeholder="如：2026.11.20" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="主承办单位">
          <el-input
            v-model="editForm.organizer"
            placeholder="如：主办：XX公司 ｜ 承办：YY机构"
          />
        </el-form-item>

        <el-form-item label="上传HTML文件">
          <el-upload
            ref="uploadRef"
            action="#"
            :auto-upload="false"
            :limit="1"
            accept=".html,.htm"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-button type="primary" plain>选择本地 HTML 邀请函文件上传</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持上传单文件 .html 页面到服务器，上传后将自动同步更新线上访问地址。
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item label="HTML源码编辑">
          <el-input
            v-model="editForm.content"
            type="textarea"
            :rows="10"
            placeholder="也可直接在此查看或编辑邀请函 HTML 源码（保存后实时生效）"
            style="font-family: Consolas, monospace; font-size: 12px"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSaveNicoInvitation">
          保存到服务器
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, RefreshLeft, Upload, Iphone, List, Edit
} from '@element-plus/icons-vue'
import {
  getNicoInvitationList,
  getNicoInvitationDetail,
  createNicoInvitation,
  updateNicoInvitation,
  deleteNicoInvitation
} from '../../api/nico-invitation'

// H5 端（如 /1.html）专用跳转的邀请函 slug，留空则不显示该快捷入口
const H5_INVITE_SLUG = ''

const router = useRouter()
const loading = ref(false)
const nicoInvitationList = ref([])

const filters = reactive({
  keyword: '',
  status: ''
})

// 预览相关
const previewVisible = ref(false)
const previewRow = ref(null)
const previewUrl = ref('')

// 编辑/上传弹窗相关
const editVisible = ref(false)
const submitting = ref(false)
const editFormRef = ref(null)
const selectedFile = ref(null)

const editForm = reactive({
  id: null,
  title: '',
  slug: '',
  event_time: '',
  deadline: '',
  organizer: '',
  status: 'active',
  content: ''
})

const editRules = {
  title: [{ required: true, message: '请输入邀请函标题', trigger: 'blur' }],
  slug: [{ required: true, message: '请输入短路径访问标识', trigger: 'blur' }]
}

// 获取服务器上的邀请函直接访问地址
const getServerInviteUrl = (row) => {
  if (!row) return ''
  const host = window.location.hostname || 'localhost'
  const port = window.location.port
  if (port === '5173') {
    return `http://${host}:3000/invite/${row.slug || row.id}`
  }
  const targetPort = port === '8083' ? '8082' : port
  return `${window.location.protocol}//${host}${targetPort ? ':' + targetPort : ''}/invite/${row.slug || row.id}`
}

// 获取 H5 端直接访问地址
const getH5DirectUrl = () => {
  const host = window.location.hostname || 'localhost'
  const port = window.location.port
  const h5Port = port === '8083' ? '8082' : '5174'
  return `${window.location.protocol}//${host}:${h5Port}/1.html`
}

// 复制文本
const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('链接已复制到剪贴板：' + text)
  } catch {
    const input = document.createElement('input')
    input.value = text
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    ElMessage.success('链接已复制：' + text)
  }
}

const openNewTab = (url) => {
  window.open(url, '_blank')
}

// 加载列表
const fetchList = async () => {
  loading.value = true
  try {
    const res = await getNicoInvitationList({
      keyword: filters.keyword || undefined,
      status: filters.status || undefined
    })
    nicoInvitationList.value = res.data?.list || []
  } catch {
    // 错误已由拦截器处理
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchList()
}

const handleReset = () => {
  filters.keyword = ''
  filters.status = ''
  fetchList()
}

// 切换状态
const handleStatusChange = async (row, val) => {
  try {
    await updateNicoInvitation(row.id, { status: val })
    ElMessage.success(`状态已更新为：${val === 'active' ? '进行中' : '已截止'}`)
  } catch {
    row.status = val === 'active' ? 'closed' : 'active'
  }
}

// 打开手机预览
const openPreview = (row) => {
  previewRow.value = row
  previewUrl.value = `/invite/${row.slug || row.id}?t=${Date.now()}`
  previewVisible.value = true
}

// 跳转到该邀请函的预约名单
const goToSignups = (row) => {
  router.push({ path: '/signups', query: { nico_invitation_id: row.id } })
}

// 打开新增/编辑弹窗
const openEditDialog = async (row = null) => {
  selectedFile.value = null
  if (row) {
    editForm.id = row.id
    editForm.title = row.title
    editForm.slug = row.slug
    editForm.event_time = row.event_time || ''
    editForm.deadline = row.deadline || ''
    editForm.organizer = row.organizer || ''
    editForm.status = row.status || 'active'
    editForm.content = '正在加载 HTML 源码...'
    editVisible.value = true

    try {
      const res = await getNicoInvitationDetail(row.id)
      editForm.content = res.data?.content || ''
    } catch {
      editForm.content = ''
    }
  } else {
    editForm.id = null
    editForm.title = ''
    editForm.slug = `invite-${Date.now().toString().slice(-5)}`
    editForm.event_time = ''
    editForm.deadline = ''
    editForm.organizer = ''
    editForm.status = 'active'
    editForm.content = ''
    editVisible.value = true
  }
}

const handleFileChange = (uploadFile) => {
  selectedFile.value = uploadFile.raw
  // 同时读取文件内容显示在源码框中
  if (uploadFile.raw) {
    const reader = new FileReader()
    reader.onload = (e) => {
      editForm.content = e.target?.result || ''
    }
    reader.readAsText(uploadFile.raw, 'utf-8')
  }
}

const handleFileRemove = () => {
  selectedFile.value = null
}

// 保存邀请函
const handleSaveNicoInvitation = async () => {
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const formData = new FormData()
    formData.append('title', editForm.title)
    formData.append('slug', editForm.slug)
    formData.append('event_time', editForm.event_time)
    formData.append('deadline', editForm.deadline)
    formData.append('organizer', editForm.organizer)
    formData.append('status', editForm.status)

    if (selectedFile.value) {
      formData.append('file', selectedFile.value)
    } else if (editForm.content) {
      formData.append('content', editForm.content)
    }

    if (editForm.id) {
      await updateNicoInvitation(editForm.id, formData)
      ElMessage.success('邀请函已更新并同步至服务器')
    } else {
      await createNicoInvitation(formData)
      ElMessage.success('邀请函已上传至服务器')
    }

    editVisible.value = false
    fetchList()
  } catch {
    // 拦截器已处理
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除邀请函「${row.title}」吗？`, '删除确认', {
      type: 'warning'
    })
    await deleteNicoInvitation(row.id)
    ElMessage.success('已删除')
    fetchList()
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.table-toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.link-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.invite-link {
  color: #409eff;
  text-decoration: none;
  max-width: 210px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.invite-link:hover {
  text-decoration: underline;
}

.phone-preview-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.phone-Preview-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.phone-frame {
  width: 390px;
  height: 740px;
  border: 10px solid #1f2937;
  border-radius: 32px;
  overflow: hidden;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
  background: #faf7f0;
}

.phone-iframe {
  width: 100%;
  height: 100%;
  border: none;
}
</style>
