<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <h2>{{ isInitMode ? 'Initialize System' : 'KXY ID Generator Login' }}</h2>
        </div>
      </template>

      <el-form
        v-if="!isInitMode"
        :model="loginForm"
        :rules="loginRules"
        ref="loginFormRef"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="Username"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Password"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            @click="handleLogin"
            :loading="loading"
          >
            Login
          </el-button>
        </el-form-item>
      </el-form>

      <el-form
        v-else
        :model="initForm"
        :rules="initRules"
        ref="initFormRef"
        @submit.prevent="handleInit"
      >
        <el-alert
          title="First Time Setup"
          type="info"
          description="Please create an admin account to initialize the system."
          :closable="false"
          style="margin-bottom: 20px"
        />

        <el-form-item prop="username">
          <el-input
            v-model="initForm.username"
            placeholder="Admin Username (min 3 characters)"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="initForm.password"
            type="password"
            placeholder="Password (min 6 characters)"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirmPassword">
          <el-input
            v-model="initForm.confirmPassword"
            type="password"
            placeholder="Confirm Password"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            @click="handleInit"
            :loading="loading"
          >
            Initialize System
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '../utils/request'

const router = useRouter()
const loading = ref(false)
const isInitMode = ref(false)
const loginFormRef = ref(null)
const initFormRef = ref(null)

const loginForm = ref({
  username: '',
  password: ''
})

const initForm = ref({
  username: '',
  password: '',
  confirmPassword: ''
})

const loginRules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

const initRules = {
  username: [
    { required: true, message: 'Please enter username', trigger: 'blur' },
    { min: 3, max: 50, message: 'Username length should be 3-50 characters', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, max: 100, message: 'Password length should be 6-100 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm password', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== initForm.value.password) {
          callback(new Error('Passwords do not match'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const checkInit = async () => {
  try {
    const response = await request.get('/api/auth/check-init')
    isInitMode.value = !response.data.initialized
  } catch (error) {
    ElMessage.error('Failed to check initialization status')
  }
}

const handleLogin = () => {
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const response = await request.post('/api/auth/login', loginForm.value)
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('username', response.data.username)
        ElMessage.success('Login successful')
        router.push('/databases')
      } catch (error) {
        console.error('Login failed:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const handleInit = () => {
  initFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await request.post('/api/auth/init-user', {
          username: initForm.value.username,
          password: initForm.value.password
        })
        ElMessage.success('System initialized successfully. Please login.')
        isInitMode.value = false
        loginForm.value.username = initForm.value.username
      } catch (error) {
        console.error('Initialization failed:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  checkInit()
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}
</style>
