<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? 'Edit Database Configuration' : 'Add Database Configuration'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      :model="form"
      :rules="rules"
      ref="formRef"
      label-width="120px"
    >
      <el-form-item label="System Code" prop="system_code">
        <el-input v-model="form.system_code" placeholder="Enter system code" />
      </el-form-item>

      <el-form-item label="Database Type" prop="db_type">
        <el-select v-model="form.db_type" placeholder="Select database type" style="width: 100%">
          <el-option label="MySQL" value="mysql" />
          <el-option label="PostgreSQL" value="postgresql" />
          <el-option label="SQL Server" value="sqlserver" />
          <el-option label="Oracle" value="oracle" />
        </el-select>
      </el-form-item>

      <el-form-item label="Address" prop="db_address">
        <el-input v-model="form.db_address" placeholder="host:port (e.g., localhost:3306)" />
      </el-form-item>

      <el-form-item label="Username" prop="db_user">
        <el-input v-model="form.db_user" placeholder="Database username" />
      </el-form-item>

      <el-form-item label="Password" prop="db_password">
        <el-input
          v-model="form.db_password"
          type="password"
          placeholder="Database password"
          show-password
        />
      </el-form-item>

      <el-form-item label="Database Name" prop="db_name">
        <el-input
          v-model="form.db_name"
          placeholder="Initial database name (optional)"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">Cancel</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          {{ isEdit ? 'Update' : 'Add' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  config: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'success'])

const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const form = ref({
  system_code: '',
  db_type: '',
  db_address: '',
  db_user: '',
  db_password: '',
  db_name: ''
})

const rules = {
  system_code: [
    { required: true, message: 'Please enter system code', trigger: 'blur' }
  ],
  db_type: [
    { required: true, message: 'Please select database type', trigger: 'change' }
  ],
  db_address: [
    { required: true, message: 'Please enter database address', trigger: 'blur' }
  ],
  db_user: [
    { required: true, message: 'Please enter database username', trigger: 'blur' }
  ],
  db_password: [
    { required: true, message: 'Please enter database password', trigger: 'blur' }
  ]
}

watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
  if (newVal && props.config) {
    isEdit.value = true
    form.value = { ...props.config }
  } else {
    isEdit.value = false
    resetForm()
  }
})

watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

const resetForm = () => {
  form.value = {
    system_code: '',
    db_type: '',
    db_address: '',
    db_user: '',
    db_password: '',
    db_name: ''
  }
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleClose = () => {
  dialogVisible.value = false
  resetForm()
}

const handleSubmit = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (isEdit.value) {
          await request.put(`/api/database/${form.value.guid}`, form.value)
          ElMessage.success('Database configuration updated successfully')
        } else {
          await request.post('/api/database/add', form.value)
          ElMessage.success('Database configuration added successfully')
        }
        emit('success')
        handleClose()
      } catch (error) {
        console.error('Submit failed:', error)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
