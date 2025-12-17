import { config } from '@vue/test-utils'
import { vi } from 'vitest'

// Mock Vuetify components
config.global.stubs = {
  VNavigationDrawer: { template: '<div><slot /></div>' },
  VList: { template: '<div><slot /></div>' },
  VListItem: { template: '<div><slot /></div>' },
  VAvatar: { template: '<div><slot /></div>' },
  VCard: { template: '<div><slot /></div>' },
  VCardTitle: { template: '<div><slot /></div>' },
  VCardText: { template: '<div><slot /></div>' },
  VBtn: { template: '<button><slot /></button>' },
  VTextField: { template: '<input />' },
  VCheckbox: { template: '<input type="checkbox" />' },
  VRadioGroup: { template: '<div><slot /></div>' },
  VRadio: { template: '<input type="radio" />' },
  VProgressLinear: { template: '<div></div>' },
  VProgressCircular: { template: '<div></div>' },
  VAlert: { template: '<div><slot /></div>' },
  VIcon: { template: '<i></i>' },
  VDataTable: { template: '<table><slot /></table>' },
  VChip: { template: '<span><slot /></span>' },
  VRow: { template: '<div><slot /></div>' },
  VCol: { template: '<div><slot /></div>' },
  VForm: { template: '<form><slot /></form>' },
  VDialog: { template: '<div><slot /></div>' },
  VSnackbar: { template: '<div><slot /></div>' },
}

// Mock router
config.global.mocks = {
  $route: {
    name: 'dashboard',
    params: {},
    query: {},
  },
}
