export type AccessModule = 
  'delegate' |  
  'expense' |
  'process' |
  'reserve' |
  'review' |
  'schedule' |
  'secure'
  
export type AccessFlag =
  | 'can_view_delegate'  
  | 'can_view_expense'
  | 'can_view_process'
  | 'can_view_reserve'
  | 'can_view_reserve_admin'
  | 'can_view_review'
  | 'can_view_schedule'
  | 'can_view_secure'
  | 'can_view_secure_admin'
  | 'is_manager'
  | 'is_is_employee'
  | 'is_fiscal_employee'
  | 'is_eligible_for_telework_application'
  | 'has_workflow_roles'
  | 'can_view_mow_routes'

export interface AccessRule {
  // The access rule is satisfied if the user has either the organization module
  // or the group permission
  module?: AccessModule
  flag?: AccessFlag
}

export interface AccessProfile {
  can_view_delegate: boolean
  can_view_expense: boolean
  can_view_schedule: boolean
  can_view_secure: boolean
  can_view_secure_admin: boolean
  can_view_process: boolean
  can_view_reserve: boolean
  can_view_reserve_admin: boolean
  can_view_review: boolean
  is_manager: boolean
  is_is_employee: boolean
  is_fiscal_employee: boolean
  is_eligible_for_telework_application: boolean
  workflow_roles: Array<number>
  is_expense_submitter: boolean
  is_expense_approver: boolean
  is_division_director: boolean
  can_view_mow_routes: boolean
  organizationModules: Array<string>
}

function normalizeModuleName (moduleName: string): string {
  return moduleName.trim().toLowerCase()
}

const accessChecks: Record<AccessFlag, (profile: AccessProfile) => boolean> = {
  can_view_delegate: profile => profile.can_view_delegate,
  can_view_expense: profile => {
    return (
      profile.is_expense_submitter ||
      profile.is_expense_approver ||
      profile.is_division_director ||
      profile.is_fiscal_employee
    )
  },
  can_view_process: profile => profile.can_view_process,
  can_view_reserve: profile => profile.can_view_reserve,
  can_view_reserve_admin: profile => profile.can_view_reserve_admin,
  can_view_review: profile => profile.can_view_review,
  can_view_schedule: profile => profile.can_view_schedule,
  can_view_secure: profile => profile.can_view_secure,
  can_view_secure_admin: profile => profile.can_view_secure_admin,
  is_manager: profile => profile.is_manager,
  is_is_employee: profile => profile.is_is_employee,
  is_fiscal_employee: profile => profile.is_fiscal_employee,
  is_eligible_for_telework_application: profile => {
    return profile.is_eligible_for_telework_application
  },
  has_workflow_roles: profile => profile.workflow_roles.length > 0,
  can_view_mow_routes: profile => profile.can_view_mow_routes
}

function hasModuleAccess (
  profile: AccessProfile,
  moduleName: string
): boolean {
  const normalizedModuleName = normalizeModuleName(moduleName)
  return profile.organizationModules.some(module => {
    return normalizeModuleName(module) === normalizedModuleName
  })
}

export function hasAccessFlag (
  profile: AccessProfile,
  flag: AccessFlag
): boolean {
  return accessChecks[flag](profile)
}

export function hasAccessRule (
  profile: AccessProfile,
  rule?: AccessRule
): boolean {
  if (!rule) {
    return true
  }

  if (
    rule.module && hasModuleAccess(profile, rule.module)
  ) {
    console.log(`Org access: ${rule.module}`)
    return true
  }

  if (rule.flag && hasAccessFlag(profile, rule.flag)) {
    console.log(`Individual access: ${rule.flag}`)
    return true
  }

  console.log(`No access: ${rule.module}`)
  return false
}