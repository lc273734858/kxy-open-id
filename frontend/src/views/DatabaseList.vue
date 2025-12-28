<template>
  <div class="database-list-container">
    <NavBar />

    <div class="content">
      <div class="toolbar">
        <h2>Database Configurations</h2>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          Add Database
        </el-button>
      </div>

      <el-table
        :data="databases"
        v-loading="loading"
        border
        style="width: 100%"
      >
        <el-table-column prop="system_code" label="System Code" width="150" />
        <el-table-column prop="db_type" label="DB Type" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.db_type.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="db_address" label="Address" width="200" />
        <el-table-column prop="db_user" label="Username" width="150" />
        <el-table-column prop="db_name" label="Database Name" width="150" />
        <el-table-column prop="guid" label="GUID" width="280" show-overflow-tooltip />
        <el-table-column label="Actions" fixed="right" width="400">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="handleView(row)">
                <el-icon><View /></el-icon>
                View
              </el-button>
              <el-button size="small" type="primary" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                Edit
              </el-button>
              <el-button size="small" type="success" @click="handleInitialize(row)">
                <el-icon><RefreshRight /></el-icon>
                Initialize
              </el-button>
              <el-button size="small" type="warning" @click="handleAddConfig(row)">
                <el-icon><Setting /></el-icon>
                Add Config
              </el-button>
              <el-button size="small" type="danger" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
                Delete
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <DatabaseForm
      v-model:visible="formVisible"
      :config="currentConfig"
      @success="loadDatabases"
    />

    <el-dialog
      v-model="viewVisible"
      title="Database Configuration Details"
      width="600px"
    >
      <el-descriptions :column="1" border v-if="currentConfig">
        <el-descriptions-item label="GUID">{{ currentConfig.guid }}</el-descriptions-item>
        <el-descriptions-item label="System Code">{{ currentConfig.system_code }}</el-descriptions-item>
        <el-descriptions-item label="Database Type">{{ currentConfig.db_type }}</el-descriptions-item>
        <el-descriptions-item label="Address">{{ currentConfig.db_address }}</el-descriptions-item>
        <el-descriptions-item label="Username">{{ currentConfig.db_user }}</el-descriptions-item>
        <el-descriptions-item label="Database Name">{{ currentConfig.db_name || 'N/A' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <el-dialog
      v-model="configVisible"
      title="Add Custom Configuration"
      width="500px"
    >
      <el-form :model="configForm" ref="configFormRef" label-width="120px">
        <el-form-item label="Field Name" prop="field_name">
          <el-input v-model="configForm.field_name" placeholder="Enter field name" />
        </el-form-item>
        <el-form-item label="Initial Value" prop="initial_value">
          <el-input-number v-model="configForm.initial_value" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitAddConfig" :loading="configLoading">Add</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Edit, Delete, RefreshRight, Setting } from '@element-plus/icons-vue'
import NavBar from '../components/NavBar.vue'
import DatabaseForm from '../components/DatabaseForm.vue'
import request from '../utils/request'

const loading = ref(false)
const databases = ref([])
const formVisible = ref(false)
const viewVisible = ref(false)
const configVisible = ref(false)
const currentConfig = ref(null)
const configLoading = ref(false)
const configFormRef = ref(null)

const configForm = ref({
  guid: '',
  field_name: '',
  initial_value: 0
})

const loadDatabases = async () => {
  loading.value = true
  try {
    const response = await request.get('/api/database/list')
    databases.value = response.data
  } catch (error) {
    console.error('Failed to load databases:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  currentConfig.value = null
  formVisible.value = true
}

const handleView = (row) => {
  currentConfig.value = row
  viewVisible.value = true
}

const handleEdit = (row) => {
  currentConfig.value = row
  formVisible.value = true
}

const handleInitialize = async (row) => {
  try {
    await ElMessageBox.confirm(
      `This will scan all tables in the database and initialize segment configurations. Continue?`,
      'Initialize Database',
      {
        confirmButtonText: 'Initialize',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
    )

    loading.value = true
    const response = await request.post(`/api/database/initialize/${row.guid}`)
    ElMessage.success(`Initialized ${response.data.initialized_count} segments successfully`)
    loadDatabases()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Initialize failed:', error)
    }
  } finally {
    loading.value = false
  }
}

const handleAddConfig = (row) => {
  currentConfig.value = row
  configForm.value = {
    guid: row.guid,
    field_name: '',
    initial_value: 0
  }
  configVisible.value = true
}

const submitAddConfig = async () => {
  configLoading.value = true
  try {
    await request.post(`/api/database/${configForm.value.guid}/add-config`, configForm.value)
    ElMessage.success('Custom configuration added successfully')
    configVisible.value = false
  } catch (error) {
    console.error('Add config failed:', error)
  } finally {
    configLoading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `This will permanently delete the database configuration and all related segments. Continue?`,
      'Delete Database',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
    )

    loading.value = true
    await request.delete(`/api/database/${row.guid}`)
    ElMessage.success('Database configuration deleted successfully')
    loadDatabases()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDatabases()
})
</script>

<style scoped>
.database-list-container {
  min-height: 100vh;
  background-color: #f0f2f5;
}

.content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.toolbar h2 {
  margin: 0;
  color: #333;
}
</style>
