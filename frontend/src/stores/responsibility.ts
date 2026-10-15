import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from '@/stores/index'
import {
  EmployeeResponsibilitiesInterface, Responsibility, ResponsibilityCreate,
  ResponsibilityNameUpdate, ResponsibilityTagRetrieve, ResponsibilityTagCreate,
  ResponsibilityTagUpdate, ResponsibilityUpdate, SimpleResponsibilityTagRetrieve
} from '@/types'

export const useResponsibilityStore = defineStore('responsibility', {
  state: () => ({
    allResponsibilities: [] as Array<Responsibility>,
    orphanedResponsibilities: [] as Array<Responsibility>,
    employeePrimaryResponsibilities: [] as Array<EmployeeResponsibilitiesInterface>,
    employeeSecondaryResponsibilities: [] as Array<EmployeeResponsibilitiesInterface>,
    tagWithResponsibilities: {} as ResponsibilityTagRetrieve,
    allTags: [] as Array<ResponsibilityTagRetrieve>,
    simpleTagList: [] as Array<SimpleResponsibilityTagRetrieve>,
  }),

  getters: {},

  actions: {
    createResponsibility(data: ResponsibilityCreate) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilities`, data, method: 'POST' })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error creating responsibility', e)
          })
      })
    },
    getAllResponsibilities() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilities` })
          .then((resp: {data: {results: Array<Responsibility>}}) => {
            this.allResponsibilities = resp.data.results
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting all responsibilities', e)
          })
      })
    },
    getOrphanedResponsibilities() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilities?orphaned=true` })
          .then((resp: {data: {results: Array<Responsibility>}}) => {
            this.orphanedResponsibilities = resp.data.results
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting orphaned responsibilities', e
            )
          })
      })
    },
    getEmployeePrimaryResponsibilities(data: {pk: string}) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilities?employee=${ data.pk }` })
          .then(resp => {
            const responsibilities: Array<Responsibility> = resp.data.results
            const employeeResponsibilities = this.employeePrimaryResponsibilities
            const thisEmployeeResponsibilities = employeeResponsibilities.filter(employeeObj => employeeObj.pk == data.pk)[0]
            if (thisEmployeeResponsibilities) {
              thisEmployeeResponsibilities.responsibilities = responsibilities
            } else {
              const employeeResponsibilitiesObj: EmployeeResponsibilitiesInterface = {pk: data.pk, responsibilities}
              employeeResponsibilities.push(employeeResponsibilitiesObj)
            }
            this.employeePrimaryResponsibilities = employeeResponsibilities
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting employee primary responsibilities', e
            )
          })
      })
    },
    getEmployeeSecondaryResponsibilities(data: {pk: string}) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilities?employee=${ data.pk }&secondary=true` })
          .then(resp => {
            const responsibilities: Array<Responsibility> = resp.data.results
            const employeeResponsibilities = this.employeeSecondaryResponsibilities
            const thisEmployeeResponsibilities = employeeResponsibilities.filter(employeeObj => employeeObj.pk == data.pk)[0]
            if (thisEmployeeResponsibilities) {
              thisEmployeeResponsibilities.responsibilities = responsibilities
            } else {
              const employeeResponsibilitiesObj: EmployeeResponsibilitiesInterface = {pk: data.pk, responsibilities}
              employeeResponsibilities.push(employeeResponsibilitiesObj)
            }
            this.employeeSecondaryResponsibilities = employeeResponsibilities
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(
              reject, 'Error getting employee secondary responsibilities', e
            )
          })
      })
    },
    updateResponsibility(pk: string, data: ResponsibilityUpdate) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilities/${pk}`, data, method: 'PUT' })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error updating responsibility', e)
          })
      })
    },
    updateResponsibilityName(data: ResponsibilityNameUpdate) {
      this.allResponsibilities.filter(r => r.pk == data.pk)[0].name = data.name
    },
    deleteResponsibility(pk: string) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilities/${pk}`, method: 'DELETE' })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error deleting responsibility', e)
          })
      })
    },

    //////////
    // Tags //
    //////////

    createTag(pk: string, data: ResponsibilityTagCreate) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilitytags`, data, method: 'POST' })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error creating tag', e)
          })
      })
    },
    getAllTags() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilitytags` })
          .then(resp => {
            this.allTags = resp.data.results
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting all tags', e)
          })
      })
    },
    getTagWithResponsibilities(pk: string) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilitytags/${ pk }` })
          .then(resp => {
            this.tagWithResponsibilities = resp.data
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting tag responsibilities', e)
          })
      })
    },
    getSimpleTagList() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilitytags/simple_list`})
          .then(resp => {
            this.simpleTagList = resp.data
            resolve('Successfully got simple tag list')
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting simple tag list', e)
          })
      })
    },
    updateTag(pk: string, data: ResponsibilityTagUpdate) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilitytags/${pk}`, data, method: 'PUT' })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error updating tag', e)
          })
      })
    },
    deleteTag(pk: string) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/responsibilitytags/${pk}`, method: 'DELETE' })
          .then(resp => {
            resolve(resp)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error deleting tag', e)
          })
      })
    },

    authLogout() {
      return new Promise((resolve) => {
        this.$reset()
        resolve('Successfully triggered logout')
      })
    }
  }
})
