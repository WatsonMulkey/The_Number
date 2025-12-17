import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'theNumberTheme',
    themes: {
      theNumberTheme: {
        dark: false,
        colors: {
          primary: '#87986A', // Sage green from design
          secondary: '#625B71',
          background: 'rgba(135, 152, 106, 0.83)',
          surface: '#FFFFFF',
          'primary-container': '#EADDFF',
          'on-primary-container': '#4F378A',
          'secondary-container': '#E8DEF8',
          'on-secondary-container': '#4A4459',
          'surface-variant': '#E7E0EC',
          'on-surface-variant': '#49454F',
        },
      },
    },
  },
})
