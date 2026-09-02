import pluginVue from 'eslint-plugin-vue'
import { withVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'

export default withVueTs(
  {
    ignores: [
      'dist/**',
    ],
  },

  pluginVue.configs['flat/recommended'],

  vueTsConfigs.recommended,
)