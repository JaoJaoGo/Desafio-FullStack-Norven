<script lang="ts">
import { defineComponent } from 'vue'

import { ApiError } from '@/services/api'
import { fornecedorService } from '@/services/fornecedorService'
import { geografiaService } from '@/services/geografiaService'

import type { Cidade, Estado, Pais } from '@/types/geografia'
import type { FornecedorCreatePayload, FornecedorUpdatePayload } from '@/types/fornecedor'

type ValidationRule = (value: unknown) => true | string

interface FormReference {
    validate: () => Promise<{ valid: boolean }>
}

interface SelectOption {
    title: string
    value: number
}

export default defineComponent({
    name: 'FornecedorFormView',

    data() {
        return {
            loading: false,
            saving: false,
            errorMessage: '',

            paises: [] as Pais[],
            estados: [] as Estado[],
            cidades: [] as Cidade[],

            loadingPaises: false,
            loadingEstados: false,
            loadingCidades: false,

            form: {
                nome: '',
                cnpj: '',

                contato: {
                    cod_pais: '',
                    ddd: '',
                    numero: '',
                },

                endereco: {
                    logradouro: '',
                    numero: '',
                    complemento: '',
                    cep: '',
                    bairro: '',

                    municipio_id: null as number | null,
                },

                pais_id: null as number | null,
                estado_id: null as number | null,
            },
        }
    },

    computed: {
        isEditMode(): boolean {
            return this.$route.name === 'fornecedor-edit'
        },

        fornecedorId(): number | null {
            if (!this.isEditMode) {
                return null
            }

            const id = Number(this.$route.params.id)

            return Number.isInteger(id) && id > 0 ? id : null
        },

        pageTitle(): string {
            return this.isEditMode ? 'Editar fornecedor' : 'Adicionar fornecedor'
        },

        pageDescription(): string {
            return this.isEditMode ? 'Salvar alterações' : 'Cadastrar fornecedor'
        },

        submitLabel(): string {
            return this.isEditMode ? 'Salvar alterações' : 'Cadastrar fornecedor'
        },

        paisOptions(): SelectOption[] {
            return this.paises.map((pais) => ({
                value: pais.id,

                title: pais.nome_pt ?? pais.nome ?? pais.sigla ?? `País ${pais.id}`,
            }))
        },

        estadoOptions(): SelectOption[] {
            return this.estados.map((estado) => ({
                value: estado.id,

                title: estado.uf ? `${estado.nome ?? ''} (${estado.uf})` : estado.nome ?? `Estado ${estado.id}`,
            }))
        },

        cidadeOptions(): SelectOption[] {
            return this.cidades.map((cidade) => ({
                value: cidade.id,

                title: cidade.nome ?? `Cidade ${cidade.id}`,
            }))
        },

        requiredRules(): ValidationRule[] {
            return [
                (value: unknown) => {
                    if (value === null || value === undefined || String(value).trim() === '') {
                        return 'Campo obrigatório.'
                    }

                    return true
                },
            ]
        },

        cnpjRules(): ValidationRule[] {
            return [
                ...this.requiredRules,

                (value: unknown) => {
                    const digits = String(value ?? '').replace(/\D/g, '')

                    return digits.length === 14 || 'O CNPJ deve possuir 14 dígitos.'
                },
            ]
        },

        cepRules(): ValidationRule[] {
            return [
                ...this.requiredRules,

                (value: unknown) => /^\d{5}-\d{3}$/.test(String(value)) || 'Informe o CEP no formato 00000-000.',
            ]
        },
    },

    mounted() {
        void this.initialize()
    },

    methods: {
        async initialize(): Promise<void> {
            this.loading = true
            this.errorMessage = ''

            try {
                await this.loadPaises()

                if (this.isEditMode) {
                    await this.loadFornecedor()
                }
            } catch (error: unknown) {
                this.handleError(error, 'Não foi possível carregar o formulário.')
            } finally {
                this.loading = false
            }
        },

        async loadPaises(): Promise<void> {
            this.loadingPaises = true

            try {
                this.paises = await geografiaService.listPaises()
            } finally {
                this.loadingPaises = false
            }
        },

        async loadEstados(paisId: number): Promise<void> {
            this.loadingEstados = true

            try {
                this.estados = await geografiaService.listEstados(paisId)
            } finally {
                this.loadingEstados = false
            }
        },

        async loadCidades(estadoId: number): Promise<void> {
            this.loadingCidades = true

            try {
                this.cidades = await geografiaService.listCidades(estadoId)
            } finally {
                this.loadingCidades = false
            }
        },

        async loadFornecedor(): Promise<void> {
            const fornecedorId = this.fornecedorId

            if (!fornecedorId) {
                throw new Error('Fornecedor inválido.')
            }

            const fornecedor = await fornecedorService.findById(fornecedorId)
            const hierarquia = await geografiaService.findCidadeHierarquia(fornecedor.endereco.municipio_id)

            this.form.nome = fornecedor.nome
            this.form.cnpj = this.formatCnpj(fornecedor.cnpj)
            this.form.contato = {
                cod_pais: fornecedor.contato.cod_pais,
                ddd: fornecedor.contato.ddd,
                numero: fornecedor.contato.numero,
            }
            this.form.endereco = {
                logradouro: fornecedor.endereco.logradouro,
                numero: fornecedor.endereco.numero,
                complemento: fornecedor.endereco.complemento ?? '',
                cep: fornecedor.endereco.cep,
                bairro: fornecedor.endereco.bairro,
                municipio_id: hierarquia.cidade.id,
            }
            this.form.pais_id = hierarquia.pais.id
            await this.loadEstados(hierarquia.pais.id)

            this.form.estado_id = hierarquia.estado.id
            await this.loadCidades(hierarquia.estado.id)
        },

        async onPaisChange(paisId: number | null): Promise<void> {
            this.form.estado_id = null
            this.form.endereco.municipio_id = null

            this.estados = []
            this.cidades = []

            if (!paisId) {
                return
            }

            try {
                await this.loadEstados(paisId)
            } catch (error: unknown) {
                this.handleError(error, 'Não foi possível carregar os estados.')
            }
        },

        async onEstadoChange(estadoId: number | null): Promise<void> {
            this.form.endereco.municipio_id = null

            this.cidades = []

            if (!estadoId) {
                return
            }

            try {
                await this.loadCidades(estadoId)
            } catch (error: unknown) {
                this.handleError(error, 'Não foi possível carregar as cidades.')
            }
        },

        formatCnpj(value: string): string {
            const digits = value.replace(/\D/g, '').slice(0, 14)

            return digits.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{0,2})$/, (_match, p1, p2, p3, p4, p5) => {
                let result = `${p1}.${p2}.${p3}/${p4}`

                if (p5) {
                    result += `-${p5}`
                }

                return result
            })
        },

        updateCnpj(value: string | null): void {
            const digits = String(value ?? '').replace(/\D/g, '').slice(0, 14)

            if (digits.length <= 2) {
                this.form.cnpj = digits
                return
            }

            if (digits.length <= 5) {
                this.form.cnpj = `${digits.slice(0, 2)}.${digits.slice(2)}`
                return
            }

            if (digits.length <= 8) {
                this.form.cnpj = `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5)}`
                return
            }

            if (digits.length <= 12) {
                this.form.cnpj = `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8)}`
                return
            }

            this.form.cnpj = `${digits.slice(0, 2)}.${digits.slice(2, 5)}.${digits.slice(5, 8)}/${digits.slice(8, 12)}-${digits.slice(12)}`
        },

        updateCep(value: string | null): void {
            const digits = String(value ?? '').replace(/\D/g, '').slice(0, 8)

            if (digits.length <= 5) {
                this.form.endereco.cep = digits

                return
            }

            this.form.endereco.cep = `${digits.slice(0, 5)}-${digits.slice(5)}`
        },

        buildPayload(): FornecedorCreatePayload {
            return {
                nome: this.form.nome.trim(),
                cnpj: this.form.cnpj.replace(/\D/g, ''),

                contato: {
                    cod_pais: this.form.contato.cod_pais.trim(),
                    ddd: this.form.contato.ddd.trim(),
                    numero: this.form.contato.numero.trim(),
                },

                endereco: {
                    logradouro: this.form.endereco.logradouro.trim(),
                    numero: this.form.endereco.numero.trim(),
                    complemento: this.form.endereco.complemento.trim() || null,
                    cep: this.form.endereco.cep.trim(),
                    bairro: this.form.endereco.bairro.trim(),

                    municipio_id: Number(this.form.endereco.municipio_id),
                },
            }
        },

        async submit(): Promise<void> {
            this.errorMessage = ''

            const form = this.$refs.form as FormReference
            const validation = await form.validate()

            if (!validation.valid) {
                return
            }

            this.saving = true

            try {
                const payload = this.buildPayload()

                if (this.isEditMode) {
                    const fornecedorId = this.fornecedorId

                    if (!fornecedorId) {
                        throw new Error('Fornecedor inválido.')
                    }

                    await fornecedorService.update(fornecedorId, payload as FornecedorUpdatePayload)
                } else {
                    await fornecedorService.create(payload)
                }

                await this.$router.push({ name: 'fornecedores' })
            } catch (error: unknown) {
                this.handleError(error, this.isEditMode ? 'Não foi possível atualizar o fornecedor.' : 'Não foi possível cadastrar o fornecedor.')
            } finally {
                this.saving = false
            }
        },

        handleError(error: unknown, fallback: string): void {
            if (error instanceof ApiError) {
                this.errorMessage = error.message

                return
            }

            this.errorMessage = fallback
        },

        async cancel(): Promise<void> {
            await this.$router.push({ name: 'fornecedores' })
        },
    },
})
</script>

<template>
  <v-container class="py-8">
    <div class="page-header mb-6">
      <div class="d-flex align-center ga-4">
        <v-btn
          icon="mdi-arrow-left"
          variant="text"
          title="Voltar"
          @click="cancel"
        />

        <div>
          <h1 class="text-h4 font-weight-bold">
            {{ pageTitle }}
          </h1>

          <p class="text-body-l text-medium-emphasis mt-2">
            {{ pageDescription }}
          </p>
        </div>
      </div>
    </div>

    <v-alert
      v-if="errorMessage"
      type="error"
      variant="tonal"
      closable
      class="mb-6"
      @click:close="errorMessage = ''"
    >
      {{ errorMessage }}
    </v-alert>

    <v-progress-linear
      v-if="loading"
      indeterminate
      class="mb-6"
    />

    <v-form
      v-else
      ref="form"
      @submit.prevent="submit"
    >
      <v-card
        rounded="xl"
        variant="outlined"
        class="mb-6"
      >
        <v-card-title class="pa-6 pb-2">
          Dados do fornecedor
        </v-card-title>

        <v-card-subtitle class="px-6">
          Informações de identificação do fornecedor.
        </v-card-subtitle>

        <v-card-text class="pa-6">
          <v-row>
            <v-col
              cols="12"
              md="6"
            >
              <v-text-field
                v-model="form.nome"
                label="Nome"
                variant="outlined"
                maxlength="50"
                :rule="requiredRules"
                required
              />
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <v-text-field
                :model="form.cnpj"
                label="CNPJ"
                variant="outlined"
                maxlength="18"
                inputmode="numeric"
                placeholder="00.000.000/0000-00"
                :rules="cnpjRules"
                required
                @update:model-value="updateCnpj"
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card
        rounded="xl"
        variant="outlined"
        class="mb-6"
      >
        <v-card-title class="pa-6 pb-2">
          Contato
        </v-card-title>
        <v-card-subtitle class="px-6">
          Telefone de contato do fornecedor.
        </v-card-subtitle>
        <v-card-text class="pa-6">
          <v-row>
            <v-col
              cols="12"
              md="3"
            >
              <v-text-field
                v-model="form.contato.cod_pais"
                label="Código do país"
                prefix="+"
                variant="outlined"
                maxlength="5"
                inputmode="numeric"
                :rules="requiredRules"
                required
              />
            </v-col>
            <v-col
              cols="12"
              md="3"
            >
              <v-text-field
                v-model="form.contato.ddd"
                label="DDD"
                variant="outlined"
                maxlength="3"
                inputmode="numeric"
                :rules="requiredRules"
                required
              />
            </v-col>
            <v-col
              cols="12"
              md="6"
            >
              <v-text-field
                v-model="form.contato.numero"
                label="Número"
                variant="outlined"
                maxlength="15"
                inputmode="numeric"
                :rules="requiredRules"
                required
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <v-card
        rounded="xl"
        variant="outlined"
        class="mb-6"
      >
        <v-card-title class="pa-6 pb-2">
          Endereço
        </v-card-title>
        <v-card-subtitle class="px-6">
          Localização do fornecedor.
        </v-card-subtitle>
        <v-card-text class="pa-6">
          <v-row>
            <v-col
              cols="12"
              md="4"
            >
              <v-select
                v-model="form.pais_id"
                :items="paisOptions"
                label="País"
                variant="outlined"
                :loading="loadingPaises"
                :disabled="loadingPaises"
                :rules="requiredRules"
                required
                @update:model-value="onPaisChange"
              />
            </v-col>
            <v-col
              cols="12"
              md="4"
            >
              <v-select
                v-model="form.estado_id"
                :items="estadoOptions"
                label="Estado"
                variant="outlined"
                :loading="loadingEstados"
                :disabled="!form.pais_id || loadingEstados"
                :rules="requiredRules"
                required
                @update:model-value="onEstadoChange"
              />
            </v-col>
            <v-col
              cols="12"
              md="4"
            >
              <v-select
                v-model="form.endereco.municipio_id"
                :items="cidadeOptions"
                label="Cidade"
                variant="outlined"
                :loading="loadingCidades"
                :disabled="!form.estado_id || loadingCidades"
                :rules="requiredRules"
                required
              />
            </v-col>
            <v-col
              cols="12"
              md="4"
            >
              <v-text-field
                :model-value="form.endereco.cep"
                label="CEP"
                variant="outlined"
                maxlength="9"
                inputmode="numeric"
                :rules="cepRules"
                required
                @update:model-value="updateCep"
              />
            </v-col>
            <v-col
              cols="12"
              md="8"
            >
              <v-text-field
                v-model="form.endereco.logradouro"
                label="Logradouro"
                variant="outlined"
                maxlength="100"
                :rules="requiredRules"
                required
              />
            </v-col>
            <v-col
              cols="12"
              md="3"
            >
              <v-text-field
                v-model="form.endereco.numero"
                label="Número"
                variant="outlined"
                maxlength="10"
                :rules="requiredRules"
                required
              />
            </v-col>
            <v-col
              cols="12"
              md="4"
            >
              <v-text-field
                v-model="form.endereco.bairro"
                label="Bairro"
                variant="outlined"
                maxlength="50"
                :rules="requiredRules"
                required
              />
            </v-col>
            <v-col
              cols="12"
              md="5"
            >
              <v-text-field
                v-model="form.endereco.complemento"
                label="Complemento"
                variant="outlined"
                maxlength="50"
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>

      <div class="form-actions">
        <v-btn
          variant="text"
          size="large"
          :disabled="saving"
          @click="cancel"
        >
          Cancelar
        </v-btn>

        <v-btn
          type="submit"
          size="large"
          prepend-icon="mdi-content-save-outline"
          :loading="saving"
          :disabled="saving"
        >
          {{ submitLabel }}
        </v-btn>
      </div>
    </v-form>
  </v-container>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-bottom: 32px;
}

@media (max-width: 700px) {
  .form-actions {
    flex-direction: column-reverse;
  }

  .form-actions :deep(.v-btn) {
    width: 100%;
  }
}
</style>