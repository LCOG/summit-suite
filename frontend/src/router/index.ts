import { route } from 'quasar/wrappers'
import { RouteLocationNormalized } from 'vue-router'
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router'

import routes from 'src/router/routes'
import { useUserStore } from 'src/stores/user'
import { hasAccessRule, type AccessRule } from 'src/utils/access'

import {
  canViewTimeOffRequest, isAuthenticated, isDivisionDirector, isExpenseApprover,
  isExpenseSubmitter, isFiscal, isHROrDirector, isManager 
} from './guards'

interface RouteMetaWithAccess {
  access?: AccessRule
  requiresAuth?: boolean
  requiresCanViewTimeOffRequest?: boolean
  requiresHROrDirector?: boolean
}

function getRouteAccessRule (to: RouteLocationNormalized) {
  const leafRoute = to.matched[to.matched.length - 1]
  return (leafRoute?.meta as RouteMetaWithAccess | undefined)?.access
}

function isPublicRoute (path: string): boolean {
  return path === '/dashboard' || path === '/auth/login'
}

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const routerInstance = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  routerInstance.beforeEach(async (to) => {
    const userStore = useUserStore()

    if (!userStore.isProfileLoaded) {
      await userStore.userRequest()
    }

    if (isPublicRoute(to.path)) {
      return true
    }

    if (to.meta.requiresAuth && !isAuthenticated()) {
      return '/dashboard'
    }

    const routeAccessRule = getRouteAccessRule(to)
    if (routeAccessRule && !hasAccessRule(userStore.accessProfile, routeAccessRule)) {
      return '/dashboard'
    }

    if (to.meta.requiresManager && !isManager()) {
      return '/dashboard'
    }
    if (to.meta.requiresFiscal && !isFiscal()) {
      return '/dashboard'
    }
    if (to.meta.requiresDivisionDirector && !isDivisionDirector()) {
      return '/dashboard'
    }
    if (to.meta.requiresExpenseSubmitter && !isExpenseSubmitter()) {
      return '/dashboard'
    }
    if (to.meta.requiresExpenseApprover && !isExpenseApprover()) {
      return '/dashboard'
    }
    if (to.meta.requiresCanViewTimeOffRequest && !canViewTimeOffRequest(to)) {
      return '/timeoff'
    }
    if (to.meta.requiresHROrDirector && !isHROrDirector()) {
      return '/reviews/dashboard'
    }

  })

  return routerInstance
})
