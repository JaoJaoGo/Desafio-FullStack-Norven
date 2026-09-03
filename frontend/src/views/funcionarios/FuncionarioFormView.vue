<script lang="ts">
import { defineComponent } from 'vue'

import { ApiError } from '@/services/api'
import { funcionarioService } from '@/services/funcionarioService'
import { geografiaService } from '@/services/geografiaService'
import { useAuthStore } from '@/stores/auth'

import type { Cidade, Estado, Pais } from '@/types/geografia'
import type { FuncionarioCreatePayload, FuncionarioUpdatePayload, NivelAcesso } from '@/types/funcionario'

type ValidationRule = (value: unknown) => true | string

interface FormReference {
    validate: () => Promise<{
        valid: boolean
    }>
}

interface SelectOption {
    title: string
    value: number
}

export default defineComponent({
    name: 'FuncionarioFormView',

    data() {
        return {
            authStore: useAuthStore(),

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
                email: '',
                password: '',

                nivel_acesso: 'operador' as NivelAcesso,

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

            nivelAcessoOptions: [
                {
                    title: 'Administrador',
                    value: 'administrador',
                },
                {
                    title: 'Operador',
                    value: 'operador',
                },
            ],
        }
    },

    computed: {
        isEditMode(): boolean {
            return this.$route.name === 'funcionario-edit'
        },

        funcionarioId(): number | null {
            if (!this.isEditMode) {
                return null
            }

            const id = Number(this.$route.params.id)

            return Number.isInteger(id) && id > 0 ? id : null
        },

        pageTitle(): string {
            return this.isEditMode ? 'Editar funcionário' : 'Adicionar funcionário'
        },

        pageDescription(): string {
            return this.isEditMode ? 'Atualize os dados do funcionário, contato e endereço.' : 'Cadastre um novo funcionário no sistema.'
        },

        submitLabel(): string {
            return this.isEditMode ? 'Salvar alterações' : 'Cadastrar funcionário'
        },

        paisOptions(): SelectOption[] {
            return this.paises.map(pais => ({
                value: pais.id,

                title: pais.nome_pt ?? pais.nome ?? pais.sigla ?? `País ${pais.id}`
            }))
        },

        estadoOptions(): SelectOption[] {
            return this.estados.map(estado => ({
                value: estado.id,

                title: estado.uf ? `${estado.nome ?? ''} (${estado.uf})` : (estado.nome ?? `Estado ${estado.id}`),
            }))
        },

        cidadeOptions(): SelectOption[] {
            return this.cidades.map(cidade => ({
                value: cidade.id,

                title: cidade.nome ?? `Cidade ${cidade.id}`,
            }))
        },

        requiredRules(): ValidationRule[] {
            return [(value: unknown) => {
                if (value === null || value === undefined || String(value).trim() === '') {
                    return 'Campo obrigatório.'
                }

                return true
            }]
        },

        emailRules(): ValidationRule[] {
            return [
                ...this.requiredRules,

                (value: unknown) => {
                    const email = String(value)

                    const valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

                    return valid || 'Informe um e-mail válido.'
                }
            ]
        },

        passwordRules(): ValidationRule[] {
            return [
                (value: unknown) => {
                    const password = String(value ?? '')

                    if (this.isEditMode && password === '') {
                        return true
                    }

                    if (password.length < 8) {
                        return 'A senha deve possuir no mínimo 8 caracteres.'
                    }

                    if (password.length > 72) {
                        return 'A senha deve possuir no máximo 72 caracteres.'
                    }

                    return true
                }
            ]
        },

        cepRules(): ValidationRule[] {
            return [
                ...this.requiredRules,

                (value: unknown) => /^\d{5}-\d{3}$/.test(String(value)) || 'Informe o CEP no formato 00000-000.'
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
                await this.authStore.ensureCurrentUser()

                await this.loadPaises()

                if (this.isEditMode) {
                    await this.loadFuncionario()
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

        async loadFuncionario(): Promise<void> {
            const funcionarioId = this.funcionarioId

            if (!funcionarioId) {
                throw new Error('Funcionário inválido.')
            }

            if (funcionarioId === this.authStore.currentUserId) {
                await this.$router.replace({ name: 'funcionarios' })

                return
            }

            const funcionario = await funcionarioService.findById(funcionarioId)

            const hierarquia = await geografiaService.findCidadeHierarquia(funcionario.endereco.municipio_id)

            this.form.nome = funcionario.nome

            this.form.email = funcionario.email

            this.form.password = ''

            this.form.nivel_acesso = funcionario.nivel_acesso

            this.form.contato = {
                cod_pais: funcionario.contato.cod_pais,
                ddd: funcionario.contato.ddd,
                numero: funcionario.contato.numero,
            }

            this.form.endereco = {
                logradouro: funcionario.endereco.logradouro,
                numero: funcionario.endereco.numero,
                complemento: funcionario.endereco.complemento ?? '',
                cep: funcionario.endereco.cep,
                bairro: funcionario.endereco.bairro,
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
            } catch (
            error: unknown
            ) {
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
            } catch (
            error: unknown
            ) {
                this.handleError(error, 'Não foi possível carregar as cidades.')
            }
        },

        updateCep(value: string | null): void {
            const digits = String(value ?? '').replace(/\D/g, '').slice(0, 8)

            if (digits.length <= 5) {
                this.form.endereco.cep = digits
                return
            }

            this.form.endereco.cep = `${digits.slice(0, 5)}-${digits.slice(5)}`
        },

        buildCreatePayload(): FuncionarioCreatePayload {
            return {
                nome: this.form.nome.trim(),
                email: this.form.email.trim(),
                password: this.form.password,
                nivel_acesso: this.form.nivel_acesso,

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

        buildUpdatePayload(): FuncionarioUpdatePayload {
            const createPayload = this.buildCreatePayload()

            const payload:
                FuncionarioUpdatePayload = {
                nome: createPayload.nome,
                email: createPayload.email,
                nivel_acesso: createPayload.nivel_acesso,
                contato: createPayload.contato,
                endereco: createPayload.endereco,
            }

            if (this.form.password) {
                payload.password = this.form.password
            }

            return payload
        },

        async submit(): Promise<void> {
            this.errorMessage = ''

            const form = this.$refs.form as unknown as FormReference

            const validation = await form.validate()

            if (!validation.valid) {
                return
            }

            this.saving = true

            try {
                if (this.isEditMode) {
                    const funcionarioId = this.funcionarioId

                    if (!funcionarioId) {
                        throw new Error('Funcionário inválido.')
                    }

                    if (funcionarioId === this.authStore.currentUserId) {
                        this.errorMessage = 'Não é permitido editar sua própria conta.'
                        return
                    }

                    await funcionarioService.update(funcionarioId, this.buildUpdatePayload())
                } else {
                    await funcionarioService.create(this.buildCreatePayload())
                }

                await this.$router.push({ name: 'funcionarios' })
            } catch (
            error: unknown
            ) {
                this.handleError(error, this.isEditMode ? 'Não foi possível atualizar o funcionário.' : 'Não foi possível cadastrar o funcionário.')
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
            await this.$router.push({
                name: 'funcionarios',
            })
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

          <p class="text-body-1 text-medium-emphasis mt-2">
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
          Dados do funcionário
        </v-card-title>

        <v-card-subtitle class="px-6">
          Informações de acesso e identificação.
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
                maxlength="100"
                :rules="requiredRules"
                required
              />
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <v-text-field
                v-model="form.email"
                label="E-mail"
                type="email"
                variant="outlined"
                :rules="emailRules"
                required
              />
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <v-select
                v-model="form.nivel_acesso"
                :items="nivelAcessoOptions"
                label="Nível de acesso"
                variant="outlined"
                :rules="requiredRules"
                required
              />
            </v-col>

            <v-col
              cols="12"
              md="6"
            >
              <v-text-field
                v-model="form.password"
                :label="isEditMode ? 'Nova senha' : 'Senha'"
                type="password"
                variant="outlined"
                maxlength="72"
                :hint="isEditMode ? 'Deixe vazio para manter a senha atual.' : 'Mínimo de 8 caracteres.'"
                persistent-hint
                :rules="passwordRules"
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
          Telefone de contato do funcionário.
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
          Localização do funcionário.
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