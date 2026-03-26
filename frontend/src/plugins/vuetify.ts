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
          primary: '#4a7c59', // Forest green (rebrand)
          secondary: '#8fb996',
          background: '#fdfcf0', // Warm cream
          surface: '#FFFFFF',
          'on-background': '#2d3436',
          'on-surface': '#2d3436',
          'on-primary': '#FFFFFF',
          'primary-container': '#faf3dd', // Warm cream accent
          'on-primary-container': '#4a7c59',
          'secondary-container': '#faf3dd',
          'on-secondary-container': '#4a7c59',
          'surface-variant': '#faf3dd',
          'on-surface-variant': '#4a4f52',
        },
      },
    },
  },
})
