import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import {
  MileageSubmissionCreate,
  MileageSubmissionRetrieve,
  SubmissionRetrieve
} from 'src/types'

export const useSubmitStore = defineStore('submissions', {
  state: () => ({
    submissions: [] as Array<SubmissionRetrieve>,
    mileageSubmissions: [] as Array<MileageSubmissionRetrieve>,

    numToApprove: 0,
    numMileageToApprove: 0,
  }),

  actions: {
    getAllSubsForEmployee(pk: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/submission?for_employee=${pk}`
        })
          .then(resp => {
            this.submissions = resp.data.results
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error getting submissions for employee',
              e
            )
          })
      })
    },

    getAllMileageSubsForEmployee(pk: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/mileage-submission?for_employee=${pk}`
        })
          .then(resp => {
            this.mileageSubmissions = resp.data.results
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error getting mileage submissions',
              e
            )
          })
      })
    },

    getAllSubsToApprove(pk: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/submission?to_approve=${pk}`
        })
          .then(resp => {
            this.numToApprove = resp.data.results.filter(
              (sub: SubmissionRetrieve) => sub.status === 'submitted'
            ).length
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error getting submissions to approve',
              e
            )
          })
      })
    },

    getAllMileageSubsToApprove(pk: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/mileage-submission?to_approve=${pk}`
        })
          .then(resp => {
            this.numMileageToApprove = resp.data.results.filter(
              (sub: MileageSubmissionRetrieve) => {
                return sub.submission?.status === 'submitted'
              }
            ).length
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error getting mileage submissions to approve',
              e
            )
          })
      })
    },

    createMileageSubmission(data: MileageSubmissionCreate) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/mileage-submission`,
          method: 'POST',
          data
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error creating mileage submission',
              e
            )
          })
      })
    },

    approveMileageSubmission(pk: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/mileage-submission/${pk}/approve`,
          method: 'PUT',
          data: {}
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error approving mileage submission',
              e
            )
          })
      })
    },

    authLogout() {
      return new Promise((resolve) => {
        this.$reset()
        resolve('Successfully triggered logout')
      })
    },

    getMileageSubmission(pk: number): Promise<MileageSubmissionRetrieve> {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/mileage-submission/${pk}`
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error getting mileage submission',
              e
            )
          })
      })
    },

    updateMileageSubmission(pk: number, data: MileageSubmissionCreate) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/mileage-submission/${pk}`,
          method: 'PUT',
          data
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error updating mileage submission',
              e
            )
          })
      })
    }
  }
})
