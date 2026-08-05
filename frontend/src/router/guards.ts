import { RouteLocationNormalized } from 'vue-router'

import { useAuthStore } from 'src/stores/auth'
import { useUserStore } from 'src/stores/user'
import { hasAccessRule, type AccessRule } from 'src/utils/access'

function canAccess (rule: AccessRule): boolean {
  const userStore = useUserStore()
  return hasAccessRule(userStore.accessProfile, rule)
}

export function isDivisionDirector() {
  const userStore = useUserStore()
  return userStore.getEmployeeProfile.is_division_director
}

export function isExpenseSubmitter() {
  const userStore = useUserStore()
  return userStore.isExpenseSubmitter
}

export function isExpenseApprover() {
  const userStore = useUserStore()
  return userStore.isExpenseApprover
}

export function canViewTimeOffRequest(to: RouteLocationNormalized) {
  const authStore = useAuthStore()
  const userStore = useUserStore()
  const toPk = typeof to.params.pk == 'string' ? to.params.pk : to.params.pk[0]
  if (
    authStore.isAuthenticated &&
    userStore.getEmployeeProfile.time_off_requests_can_view &&
    userStore.getEmployeeProfile.time_off_requests_can_view.indexOf(
      Number(toPk)
    ) != -1
  ) {
    return true
  } else {
    return false
  }
}

export function isFiscal() {
  const userStore = useUserStore()
  return userStore.isFiscal
}

export function isManager() {
  const userStore = useUserStore()
  return userStore.isManager
}

export function isHROrDirector() {
  const userStore = useUserStore()
  return (
    userStore.getEmployeeProfile.is_hr_employee ||
    userStore.getEmployeeProfile.is_division_director ||
    userStore.getEmployeeProfile.is_executive_director
  )
}

export function isAuthenticated() {
  const authStore = useAuthStore()
  if (authStore.isAuthenticated) {
    return true
  } else {
    console.info(
      'User is not logged in. Redirecting to dashboard.'
    )
    return false
  }
}
