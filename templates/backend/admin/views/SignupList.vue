<template>
  <div class="signup-list-page">
    <!-- 顶部核心指标卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-label">累计预约单数</div>
          <div class="stat-value">{{ stats.total_orders || 0 }}</div>
          <div class="stat-sub">总预约提交记录</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card pending">
          <div class="stat-label">待教务联系跟进</div>
          <div class="stat-value">{{ stats.pending_count || 0 }}</div>
          <div class="stat-sub">新提交待电话确认</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card confirmed">
          <div class="stat-label">已确认参会单数</div>
          <div class="stat-value">{{ stats.confirmed_count || 0 }}</div>
          <div class="stat-sub">已完成席位锁定</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card people">
          <div class="stat-label">累计报名总人数</div>
          <div class="stat-value">{{ stats.total_attendees || 0 }} <span class="unit">人</span></div>
          <div class="stat-sub">按有效报名人数汇总</div>
        </div>
      </el-col>
    </el-row>

    <!-- 搜索筛选与操作栏 -->
    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
        <div class="filter-left">
          <el-select
            v-model="filters.nico_invitation_id"
            placeholder="所属邀请函"
            clearable
            style="width: 240px"
            @change="handleSearch"
          >
            <el-option
              v-for="item in nicoInvitationOptions"
              :key="item.id"
              :label="item.title"
              :value="item.id"
            />
          </el-select>

          <el-select
            v-model="filters.status"
            placeholder="跟进状态"
            clearable
            style="width: 150px"
            @change="handleSearch"
          >
            <el-option label="待联系跟进" value="pending" />
            <el-option label="已电话联系" value="contacted" />
            <el-option label="已确认参会" value="confirmed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>

          <el-input
            v-model="filters.keyword"
            placeholder="搜索姓名 / 手机号 / 企业名称 / 职务..."
            clearable
            style="width: 280px"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
        </div>

        <div class="filter-right">
          <el-button type="success" plain @click="handleExport" :loading="exporting">
            <el-icon><Download /></el-icon> 导出 CSV / Excel
          </el-button>
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon> 手动录入预约
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 预约数据表格 -->
    <el-card shadow="never" class="table-card">
      <el-table :data="list" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="65" align="center" />

        <el-table-column label="嘉宾姓名 / 职务" min-width="150">
          <template #default="{ row }">
            <div class="guest-name">{{ row.name }}</div>
            <div class="guest-position">{{ row.title || '未填职务' }}</div>
          </template>
        </el-table-column>

        <el-table-column prop="phone" label="联系电话" width="135">
          <template #default="{ row }">
            <span class="phone-num">{{ row.phone }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="company" label="企业名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="company-text">{{ row.company || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="count" label="报名人数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="warning" effect="plain" round>{{ row.count || 1 }} 人</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="note" label="关注议题 / 留言备注" min-width="190" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.note || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="nico_invitation_title" label="所属邀请函" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.nico_invitation_title || '未关联' }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="跟进状态" width="130" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" effect="light">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="admin_remark" label="教务跟进备注" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="admin-note-text">{{ row.admin_remark || '暂无跟进记录' }}</span>
          </template>
        </el-table-column>

        <el-table-column label="提交时间" width="165">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="openEditDialog(row)">
              跟进/编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 跟进/编辑/新增预约弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isAdd ? '手动录入预约报名信息' : '跟进 / 编辑预约信息'"
      width="560px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="105px">
        <el-form-item label="所属邀请函" prop="nico_invitation_id" v-if="isAdd">
          <el-select v-model="form.nico_invitation_id" placeholder="请选择邀请函" style="width: 100%">
            <el-option
              v-for="item in nicoInvitationOptions"
              :key="item.id"
              :label="item.title"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="嘉宾姓名" prop="name">
              <el-input v-model="form.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="form.phone" placeholder="请输入11位手机号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="企业名称" prop="company">
          <el-input v-model="form.company" placeholder="请输入企业完整名称" />
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="担任职务" prop="title">
              <el-input v-model="form.title" placeholder="如：董事长 / 总经理" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报名人数" prop="count">
              <el-input-number v-model="form.count" :min="1" :max="20" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="关注议题/留言">
          <el-input
            v-model="form.note"
            type="textarea"
            :rows="2"
            placeholder="嘉宾填写的关注议题或特殊行程需求"
          />
        </el-form-item>

        <el-divider content-position="left">教务组跟进信息</el-divider>

        <el-form-item label="跟进状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio-button value="pending">待联系跟进</el-radio-button>
            <el-radio-button value="contacted">已电话联系</el-radio-button>
            <el-radio-button value="confirmed">已确认参会</el-radio-button>
            <el-radio-button value="cancelled">已取消</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="教务跟进备注">
          <el-input
            v-model="form.admin_remark"
            type="textarea"
            :rows="3"
            placeholder="记录联系情况，例如：已电话确认参会意向，资料齐全，预计 X 月 X 日前完成付款..."
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="submitForm">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Download, Plus } from '@element-plus/icons-vue'
import {
  getSignupList,
  createSignup,
  updateSignup,
  deleteSignup,
  exportSignups,
  getNicoInvitationList
} from '../../api/nico-invitation'

const route = useRoute()
const loading = ref(false)
const exporting = ref(false)
const list = ref([])
const nicoInvitationOptions = ref([])

const stats = reactive({
  total_orders: 0,
  pending_count: 0,
  contacted_count: 0,
  confirmed_count: 0,
  total_attendees: 0
})

const filters = reactive({
  nico_invitation_id: route.query.nico_invitation_id ? Number(route.query.nico_invitation_id) : '',
  status: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 弹窗状态
const dialogVisible = ref(false)
const isAdd = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const form = reactive({
  id: null,
  nico_invitation_id: '',
  name: '',
  phone: '',
  company: '',
  title: '',
  count: 1,
  note: '',
  status: 'pending',
  admin_remark: ''
})

const rules = {
  name: [{ required: true, message: '请输入嘉宾姓名', trigger: 'blur' }],
  company: [{ required: true, message: '请输入企业名称', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号', trigger: 'blur' }
  ]
}

// 加载邀请函下拉选项
const loadNicoInvitationOptions = async () => {
  try {
    const res = await getNicoInvitationList()
    if (res?.success) {
      nicoInvitationOptions.value = res.data?.list || []
      if (!form.nico_invitation_id && nicoInvitationOptions.value.length > 0) {
        form.nico_invitation_id = nicoInvitationOptions.value[0].id
      }
    }
  } catch (err) {
    console.error('加载邀请函选项失败:', err)
  }
}

// 获取预约列表
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getSignupList({
      page: pagination.page,
      pageSize: pagination.pageSize,
      nico_invitation_id: filters.nico_invitation_id || undefined,
      status: filters.status || undefined,
      keyword: filters.keyword.trim() || undefined
    })
    if (res?.success) {
      list.value = res.data?.list || []
      pagination.total = res.data?.total || 0
      if (res.data?.stats) {
        Object.assign(stats, res.data.stats)
      }
    }
  } catch {
    // 错误由拦截器统一提示
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  filters.nico_invitation_id = ''
  filters.status = ''
  filters.keyword = ''
  pagination.page = 1
  fetchData()
}

// 导出 CSV
const handleExport = async () => {
  exporting.value = true
  try {
    const blobData = await exportSignups({
      nico_invitation_id: filters.nico_invitation_id || undefined,
      status: filters.status || undefined,
      keyword: filters.keyword.trim() || undefined
    })
    const blob = new Blob([blobData], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `报名信息表_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

// 打开新增弹窗
const openAddDialog = () => {
  isAdd.value = true
  Object.assign(form, {
    id: null,
    nico_invitation_id: filters.nico_invitation_id || (nicoInvitationOptions.value[0]?.id ?? ''),
    name: '',
    phone: '',
    company: '',
    title: '',
    count: 1,
    note: '',
    status: 'confirmed',
    admin_remark: '教务后台手动录入'
  })
  dialogVisible.value = true
}

// 打开跟进/编辑弹窗
const openEditDialog = (row) => {
  isAdd.value = false
  Object.assign(form, {
    id: row.id,
    nico_invitation_id: row.nico_invitation_id,
    name: row.name || '',
    phone: row.phone || '',
    company: row.company || '',
    title: row.title || '',
    count: row.count || 1,
    note: row.note || '',
    status: row.status || 'pending',
    admin_remark: row.admin_remark || ''
  })
  dialogVisible.value = true
}

// 提交保存
const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (isAdd.value) {
        const createRes = await createSignup({
          nico_invitation_id: form.nico_invitation_id,
          name: form.name,
          phone: form.phone,
          company: form.company,
          title: form.title,
          count: form.count,
          note: form.note
        })
        const newId = createRes?.data?.id
        if (newId && (form.status !== 'pending' || form.admin_remark)) {
          await updateSignup(newId, {
            status: form.status,
            admin_remark: form.admin_remark
          })
        }
        ElMessage.success('录入预约信息成功')
      } else {
        await updateSignup(form.id, {
          name: form.name,
          phone: form.phone,
          company: form.company,
          title: form.title,
          count: form.count,
          note: form.note,
          status: form.status,
          admin_remark: form.admin_remark
        })
        ElMessage.success('更新跟进状态成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch {
      // 错误由拦截器统一提示
    } finally {
      submitting.value = false
    }
  })
}

// 删除预约
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除嘉宾「${row.name}（${row.phone}）」的预约记录吗？`,
      '删除确认',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' }
    )
    await deleteSignup(row.id)
    ElMessage.success('已删除该条预约记录')
    fetchData()
  } catch (err) {
    if (err !== 'cancel') {
      // 已处理
    }
  }
}

const statusLabel = (s) => {
  const map = {
    pending: '待联系跟进',
    contacted: '已电话联系',
    confirmed: '已确认参会',
    cancelled: '已取消'
  }
  return map[s] || '待联系跟进'
}

const statusTagType = (s) => {
  const map = {
    pending: 'warning',
    contacted: 'primary',
    confirmed: 'success',
    cancelled: 'info'
  }
  return map[s] || 'warning'
}

const formatTime = (t) => {
  if (!t) return '-'
  return String(t).replace('T', ' ').slice(0, 19)
}

onMounted(() => {
  loadNicoInvitationOptions()
  fetchData()
})
</script>

<style scoped>
.signup-list-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-row {
  margin-bottom: 2px;
}

.stat-card {
  background: #fff;
  border-radius: 8px;
  padding: 18px 20px;
  border: 1px solid #ebeef5;
  border-left: 4px solid #409eff;
}

.stat-card.pending {
  border-left-color: #e6a23c;
}

.stat-card.confirmed {
  border-left-color: #67c23a;
}

.stat-card.people {
  border-left-color: #b88230;
}

.stat-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-value .unit {
  font-size: 14px;
  font-weight: 500;
  color: #909399;
}

.stat-sub {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}

.filter-card {
  border-radius: 8px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-card {
  border-radius: 8px;
}

.guest-name {
  font-weight: 600;
  color: #303133;
}

.guest-position {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.phone-num {
  font-family: monospace;
  font-weight: 600;
  color: #409eff;
}

.company-text {
  color: #303133;
}

.admin-note-text {
  color: #606266;
  font-size: 13px;
}

.pagination-wrap {
  margin-top: 18px;
  display: flex;
  justify-content: flex-end;
}
</style>
