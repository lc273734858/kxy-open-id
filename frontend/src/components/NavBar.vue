<template>
  <div class="navbar">
    <div class="navbar-content">
      <div class="navbar-left">
        <h1>KXY ID Generator</h1>
      </div>
      <div class="navbar-right">
        <span class="username">{{ username }}</span>
        <el-button type="danger" size="small" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          Logout
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const username = ref('')

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  ElMessage.success('Logged out successfully')
  router.push('/login')
}

onMounted(() => {
  username.value = localStorage.getItem('username') || 'Admin'
})
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.navbar-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
}

.navbar-left h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  font-size: 14px;
  opacity: 0.9;
}
</style>
