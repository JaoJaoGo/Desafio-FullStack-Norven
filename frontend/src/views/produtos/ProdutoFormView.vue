<script lang="ts">
import { defineComponent } from 'vue'

import { ApiError } from '@/services/api'
import { categoriaService } from '@/services/categoriaService'
import { produtoService } from '@/services/produtoService'
import { unidadeMedidaService } from '@/services/unidadeMedidaService'
import { useAuthStore } from '@/stores/auth'

import type { Categoria } from '@/types/categoria'
import type { InformacaoNutricionalPayload, ProdutoCreatePayload, ProdutoUpdatePayload } from '@/types/produto'
import type { UnidadeMedida } from '@/types/unidadeMedida'

interface FormReference {
  validate: () => Promise<{valid: boolean}>
}

interface SelectOption {
  title: string
  value: number
}

type UnidadeSelectionTarget = 'produto' | 'porcao'

export default defineComponent({
  name: 'ProdutoFormView',

  data() {
    return {
      authStore: useAuthStore(),

      loading: false,
      saving: false,
      errorMessage: '',

      categorias: [] as Categoria[],
      unidadesMedidas: [] as UnidadeMedida[],

      loadingCategorias: false,
      loadingUnidades: false,

      responsavelLabel: '',

      informacaoNutricionalEnabled: false,

      categoriaDialog: false,
      unidadeDialog: false,

      savingCategoria: false,
      savingUnidade: false,

      categoriaErrorMessage: '',
      unidadeErrorMessage: '',

      unidadeSelectionTarget: 'produto' as UnidadeSelectionTarget,

      categoriaForm: {
        nome: '',
      },

      unidadeForm: {
        nome: '',
        sigla: '',
      },

      form: {
        cod_idt: '',
        nome: '',
        descricao: '',
        preco_venda_atual: '',
        eh_perecivel: false,

        categoria_id: null as number | null,

        unidade_medida_id: null as number | null,

        informacao_nutricional: {
          porcao_quantidade: '',
          valor_energetico_kcal: '',
          carboidratos_g: '',
          proteinas_g: '',
          gorduras_totais_g: '',
          ingredientes: '',
          alergenicos: '',

          unidade_porcao_id: null as number | null,
        },
      },
    }
  },

  computed: {
    isEditMode(): boolean {
      return this.$route.name === 'produto-edit'
    },

    produtoId(): number | null {
      if (!this.isEditMode) {
        return null
      }

      const id = Number(this.$route.params.id)

      if (!Number.isInteger(id) || id <= 0) {
        return null
      }

      return id
    },

    pageTitle(): string {
      return this.isEditMode ? 'Editar produto' : 'Adicionar produto'
    },

    pageDescription(): string {
      return this.isEditMode ? 'Atualize os dados cadastrais e nutricionais do produto.' : 'Cadastre os dados básicos e nutricionais do produto.'
    },

    submitLabel(): string {
      return this.isEditMode ? 'Salvar alterações' : 'Cadastrar produto'
    },

    categoriaOptions(): SelectOption[] {
      return this.categorias.map((categoria) => ({
        title: categoria.nome,
        value: categoria.id,
      }))
    },

    unidadeOptions(): SelectOption[] {
      return this.unidadesMedidas.map((unidade) => ({
        title: `${unidade.nome} (${unidade.sigla})`,
        value: unidade.id,
      }))
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

        const currentUser = this.authStore.user

        if (currentUser) {
          this.responsavelLabel = `${currentUser.nome} (${currentUser.email})`
        }

        await Promise.all([
          this.loadCategorias(),
          this.loadUnidadesMedidas(),
        ])

        if (this.isEditMode) {
          await this.loadProduto()
        }
      } catch (error: unknown) {
        this.handleError(error, 'Não foi possível carregar o formulário.')
      } finally {
        this.loading = false
      }
    },

    async loadCategorias(): Promise<void> {
      this.loadingCategorias = true

      try {
        this.categorias = await categoriaService.listAll()
      } finally {
        this.loadingCategorias = false
      }
    },

    async loadUnidadesMedidas(): Promise<void> {
      this.loadingUnidades = true

      try {
        this.unidadesMedidas = await unidadeMedidaService.listAll()
      } finally {
        this.loadingUnidades = false
      }
    },

    async loadProduto(): Promise<void> {
      const produtoId = this.produtoId

      if (!produtoId) {
        throw new Error('Produto inválido.')
      }

      const produto = await produtoService.findById(produtoId)
      this.form.cod_idt = produto.cod_idt
      this.form.nome = produto.nome
      this.form.descricao = produto.descricao ?? ''
      this.form.preco_venda_atual = this.formatCurrencyValue(produto.preco_venda_atual)
      this.form.eh_perecivel = produto.eh_perecivel
      this.form.categoria_id = produto.categoria_id
      this.form.unidade_medida_id = produto.unidade_medida_id
      this.responsavelLabel = `${produto.responsavel.nome} (${produto.responsavel.email})`

      const informacao = produto.informacao_nutricional
      this.informacaoNutricionalEnabled = informacao !== null

      if (!informacao) {
        return
      }

      this.form.informacao_nutricional = {
        porcao_quantidade: this.decimalToInput(informacao.porcao_quantidade),
        valor_energetico_kcal: this.decimalToInput(informacao.valor_energetico_kcal),
        carboidratos_g: this.decimalToInput(informacao.carboidratos_g),
        proteinas_g: this.decimalToInput(informacao.proteinas_g),
        gorduras_totais_g: this.decimalToInput(informacao.gorduras_totais_g),
        ingredientes: informacao.ingredientes ?? '',
        alergenicos: informacao.alergenicos ?? '',
        unidade_porcao_id: informacao.unidade_porcao_id,
      }
    },

    requiredRule(value: unknown): true | string {
      if (value === null || value === undefined || String(value).trim() === '') {
        return 'Campo obrigatório.'
      }

      return true
    },

    priceRule(value: unknown): true | string {
      const numeric = this.parseCurrency(String(value ?? ''))

      if (!Number.isFinite(numeric) || numeric < 0) {
        return 'Informe um preço válido.'
      }

      if (numeric > 99_999_999.99) {
        return 'O preço deve ser menor ou igual a R$ 99.999.999,99.'
      }

      return true
    },

    positiveDecimalRule(value: unknown): true | string {
      const normalized = this.normalizeDecimalInput(value)

      if (!normalized) {
        return 'Campo obrigatório.'
      }

      if (!this.isValidDecimal(normalized, false)) {
        return 'Informe um valor maior que zero com até 2 casas decimais.'
      }

      return true
    },

    optionalDecimalRule(value: unknown): true | string {
      const normalized = this.normalizeDecimalInput(value)

      if (!normalized) {
        return true
      }

      if (!this.isValidDecimal(normalized, true)) {
        return 'Informe um valor maior ou igual a zero com até 2 casas decimais.'
      }

      return true
    },

    categoryNameRule(value: unknown): true | string {
      const text = String(value ?? '').trim()

      if (!text) {
        return 'Campo obrigatório.'
      }

      if (text.length > 30) {
        return 'O nome deve possuir no máximo 30 caracteres.'
      }

      return true
    },

    unitNameRule(value: unknown): true | string {
      const text = String(value ?? '').trim()

      if (!text) {
        return 'Campo obrigatório.'
      }

      if (text.length > 30) {
        return 'O nome deve possuir no máximo 30 caracteres.'
      }

      return true
    },

    unitSiglaRule(value: unknown): true | string {
      const text = String(value ?? '').trim()

      if (!text) {
        return 'Campo obrigatório.'
      }

      if (text.length > 5) {
        return 'A sigla deve possuir no máximo 5 caracteres.'
      }

      return true
    },

    parseCurrency(value: string): number {
      const normalized = value.replace(/\./g, '').replace(',', '.').trim()

      if (!normalized) {
        return Number.NaN
      }

      return Number(normalized)
    },

    formatCurrencyValue(value: unknown): string {
      const numeric = Number(value)

      if (!Number.isFinite(numeric)) {
        return ''
      }

      return new Intl.NumberFormat(
        'pt-BR',
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        },
      ).format(
        numeric,
      )
    },

    updatePrecoVenda(value: unknown): void {
      const digits = String(value ?? '').replace(/\D/g, '').slice(0, 10)

      if (!digits) {
        this.form.preco_venda_atual = ''
        return
      }

      const numeric = Number(digits) / 100

      this.form.preco_venda_atual = new Intl.NumberFormat(
        'pt-BR',
        {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        },
        ).format(
          numeric,
        )
    },

    normalizeDecimalInput(value: unknown): string {
      return String(value ?? '').trim().replace(',', '.')
    },

    isValidDecimal(value: string, allowZero: boolean): boolean {
      if (!/^\d+(\.\d{1,2})?$/.test(value)) {
        return false
      }

      const numeric = Number(value)

      if (!Number.isFinite(numeric) || numeric > 99_999_999.99) {
        return false
      }

      return allowZero ? numeric >= 0 : numeric > 0
    },

    decimalToInput(value: unknown): string {
      if (value === null || value === undefined) {
        return ''
      }

      return String(value).replace('.', ',')
    },

    normalizeOptionalDecimal(value: string): string | null {
      const normalized = this.normalizeDecimalInput(value)

      return normalized || null
    },

    buildInformacaoNutricional(): InformacaoNutricionalPayload | null {
      if (!this.informacaoNutricionalEnabled) {
        return null
      }

      return {
        porcao_quantidade: this.normalizeDecimalInput(this.form.informacao_nutricional.porcao_quantidade),
        valor_energetico_kcal: this.normalizeOptionalDecimal(this.form.informacao_nutricional.valor_energetico_kcal),
        carboidratos_g: this.normalizeOptionalDecimal(this.form.informacao_nutricional.carboidratos_g),
        proteinas_g: this.normalizeOptionalDecimal(this.form.informacao_nutricional.proteinas_g),
        gorduras_totais_g: this.normalizeOptionalDecimal(this.form.informacao_nutricional.gorduras_totais_g),
        ingredientes: this.form.informacao_nutricional.ingredientes.trim() || null,
        alergenicos: this.form.informacao_nutricional.alergenicos.trim() || null,
        unidade_porcao_id: Number(this.form.informacao_nutricional.unidade_porcao_id),
      }
    },

    buildCreatePayload(): ProdutoCreatePayload {
      const preco = this.parseCurrency(this.form.preco_venda_atual)

      return {
        cod_idt: this.form.cod_idt.trim(),
        nome: this.form.nome.trim(),
        descricao: this.form.descricao.trim() || null,
        preco_venda_atual: preco.toFixed(2),
        eh_perecivel: this.form.eh_perecivel,
        categoria_id: Number(this.form.categoria_id),
        unidade_medida_id: Number(this.form.unidade_medida_id),
        informacao_nutricional: this.buildInformacaoNutricional(),
      }
    },

    buildUpdatePayload(): ProdutoUpdatePayload {
      const payload = this.buildCreatePayload()

      return {
        cod_idt: payload.cod_idt,
        nome: payload.nome,
        descricao: payload.descricao,
        preco_venda_atual: payload.preco_venda_atual,
        eh_perecivel: payload.eh_perecivel,
        categoria_id: payload.categoria_id,
        unidade_medida_id: payload.unidade_medida_id,
        informacao_nutricional: payload.informacao_nutricional,
      }
    },

    async submit(): Promise<void> {
      this.errorMessage = ''

      const form = this.$refs.form as FormReference | undefined

      if (!form) {
        return
      }

      const validation = await form.validate()

      if (!validation.valid) {
        return
      }

      this.saving = true

      try {
        if (this.isEditMode) {
          const produtoId = this.produtoId

          if (!produtoId) {
            throw new Error('Produto inválido.')
          }

          await produtoService.update(produtoId, this.buildUpdatePayload())
        } else {
          await produtoService.create(this.buildCreatePayload())
        }

        await this.$router.push({ name: 'produtos' })
      } catch (error: unknown) {
        this.handleError(error, this.isEditMode ? 'Não foi possível atualizar o produto.' : 'Não foi possível cadastrar o produto.')
      } finally {
        this.saving = false
      }
    },

    openCategoriaDialog(): void {
      this.categoriaForm.nome = ''
      this.categoriaErrorMessage = ''
      this.categoriaDialog = true
    },

    closeCategoriaDialog(): void {
      if (this.savingCategoria) {
        return
      }

      this.categoriaDialog = false
      this.categoriaErrorMessage = ''
    },

    async createCategoria(): Promise<void> {
      const form = this.$refs.categoriaFormRef as FormReference | undefined

      if (!form) {
        return
      }

      const validation = await form.validate()

      if (!validation.valid) {
        return
      }

      this.savingCategoria = true
      this.categoriaErrorMessage = ''

      try {
        const categoria = await categoriaService.create({ nome: this.categoriaForm.nome.trim() })

        const categoriasSemDuplicata = this.categorias.filter((item) => item.id !== categoria.id)

        this.categorias = [...categoriasSemDuplicata, categoria].sort((first, second) => first.nome.localeCompare(second.nome, 'pt-BR'))

        this.form.categoria_id = categoria.id

        this.categoriaForm.nome = ''
        this.categoriaDialog = false
      } catch (error: unknown) {
        if (error instanceof ApiError) {
          this.categoriaErrorMessage = error.message
        } else {
          this.categoriaErrorMessage = 'Não foi possível cadastrar a categoria.'
        }
      } finally {
        this.savingCategoria = false
      }
    },

    openUnidadeDialog(target: UnidadeSelectionTarget): void {
      this.unidadeSelectionTarget = target

      this.unidadeForm = {
        nome: '',
        sigla: '',
      }

      this.unidadeErrorMessage = ''
      this.unidadeDialog = true
    },

    closeUnidadeDialog(): void {
      if (this.savingUnidade) {
        return
      }

      this.unidadeDialog = false
      this.unidadeErrorMessage = ''
    },

    async createUnidadeMedida(): Promise<void> {
      const form = this.$refs.unidadeFormRef as FormReference | undefined

      if (!form) {
        return
      }

      const validation = await form.validate()

      if (!validation.valid) {
        return
      }

      this.savingUnidade = true
      this.unidadeErrorMessage = ''

      try {
        const unidade = await unidadeMedidaService.create({
          nome: this.unidadeForm.nome.trim(),
          sigla: this.unidadeForm.sigla.trim(),
        })

        const unidadesSemDuplicata = this.unidadesMedidas.filter((item) => item.id !== unidade.id)

        this.unidadesMedidas = [...unidadesSemDuplicata, unidade].sort((first, second) => first.nome.localeCompare(second.nome, 'pt-BR'))

        if (this.unidadeSelectionTarget === 'produto') {
          this.form.unidade_medida_id = unidade.id
        } else {
          this.form.informacao_nutricional.unidade_porcao_id = unidade.id
        }

        this.unidadeForm = {
          nome: '',
          sigla: '',
        }

        this.unidadeDialog = false
      } catch (error: unknown) {
        if (error instanceof ApiError) {
          this.unidadeErrorMessage = error.message
        } else {
          this.unidadeErrorMessage = 'Não foi possível cadastrar a unidade de medida.'
        }
      } finally {
        this.savingUnidade = false
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
        name: 'produtos',
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
          Dados do produto
        </v-card-title>

        <v-card-subtitle class="px-6">
          Informações básicas para identificação
          e comercialização.
        </v-card-subtitle>

        <v-card-text class="pa-6">
          <v-row>
            <v-col
              cols="12"
              md="4"
            >
              <v-text-field
                v-model="form.cod_idt"
                label="Código identificador"
                variant="outlined"
                maxlength="50"
                :rules="[requiredRule]"
                required
              />
            </v-col>

            <v-col
              cols="12"
              md="8"
            >
              <v-text-field
                v-model="form.nome"
                label="Nome"
                variant="outlined"
                maxlength="50"
                :rules="[requiredRule]"
                required
              />
            </v-col>

            <v-col cols="12">
              <v-textarea
                v-model="form.descricao"
                label="Descrição"
                variant="outlined"
                rows="3"
                auto-grow
              />
            </v-col>

            <v-col
              cols="12"
              md="4"
            >
              <v-text-field
                :model-value="form.preco_venda_atual"
                label="Preço de venda"
                prefix="R$"
                variant="outlined"
                inputmode="numeric"
                :rules="[
                  requiredRule,
                  priceRule,
                ]"
                required
                @update:model-value="updatePrecoVenda"
              />
            </v-col>

            <v-col
              cols="12"
              md="4"
            >
              <div class="field-with-action">
                <v-select
                  v-model="form.categoria_id"
                  :items="categoriaOptions"
                  label="Categoria"
                  variant="outlined"
                  :loading="loadingCategorias"
                  :disabled="loadingCategorias"
                  :rules="[requiredRule]"
                  required
                  class="flex-grow-1"
                />

                <v-btn
                  icon="mdi-plus"
                  variant="tonal"
                  size="large"
                  title="Adicionar categoria"
                  :disabled="loadingCategorias"
                  @click="openCategoriaDialog"
                />
              </div>
            </v-col>

            <v-col
              cols="12"
              md="4"
            >
              <div class="field-with-action">
                <v-select
                  v-model="form.unidade_medida_id"
                  :items="unidadeOptions"
                  label="Unidade de medida"
                  variant="outlined"
                  :loading="loadingUnidades"
                  :disabled="loadingUnidades"
                  :rules="[requiredRule]"
                  required
                  class="flex-grow-1"
                />

                <v-btn
                  icon="mdi-plus"
                  variant="tonal"
                  size="large"
                  title="Adicionar unidade de medida"
                  :disabled="loadingUnidades"
                  @click="
                    openUnidadeDialog(
                      'produto',
                    )
                  "
                />
              </div>
            </v-col>

            <v-col
              cols="12"
              md="8"
            >
              <v-text-field
                :model-value="responsavelLabel"
                label="Responsável pelo cadastro"
                prepend-inner-icon="mdi-account-outline"
                variant="outlined"
                disabled
                persistent-hint
                hint="O responsável é definido automaticamente pela conta autenticada."
              />
            </v-col>

            <v-col
              cols="12"
              md="4"
              class="d-flex align-center"
            >
              <v-switch
                v-model="form.eh_perecivel"
                label="Produto perecível"
                hide-details
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
          Informação nutricional
        </v-card-title>

        <v-card-subtitle class="px-6">
          Preencha somente quando essas informações
          forem aplicáveis ao produto.
        </v-card-subtitle>

        <v-card-text class="pa-6">
          <v-switch
            v-model="informacaoNutricionalEnabled"
            label="Adicionar informação nutricional"
            hide-details
            class="mb-6"
          />

          <v-expand-transition>
            <div v-if="informacaoNutricionalEnabled">
              <v-row>
                <v-col
                  cols="12"
                  md="6"
                >
                  <v-text-field
                    v-model="form
                      .informacao_nutricional
                      .porcao_quantidade
                    "
                    label="Quantidade da porção"
                    variant="outlined"
                    inputmode="decimal"
                    :rules="[
                      requiredRule,
                      positiveDecimalRule,
                    ]"
                    required
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="6"
                >
                  <div class="field-with-action">
                    <v-select
                      v-model="form
                        .informacao_nutricional
                        .unidade_porcao_id
                      "
                      :items="unidadeOptions"
                      label="Unidade da porção"
                      variant="outlined"
                      :loading="loadingUnidades"
                      :disabled="loadingUnidades"
                      :rules="[requiredRule]"
                      required
                      class="flex-grow-1"
                    />

                    <v-btn
                      icon="mdi-plus"
                      variant="tonal"
                      size="large"
                      title="Adicionar unidade para a porção"
                      :disabled="loadingUnidades"
                      @click="
                        openUnidadeDialog(
                          'porcao',
                        )
                      "
                    />
                  </div>
                </v-col>

                <v-col
                  cols="12"
                  sm="6"
                  lg="3"
                >
                  <v-text-field
                    v-model="form
                      .informacao_nutricional
                      .valor_energetico_kcal
                    "
                    label="Valor energético"
                    suffix="kcal"
                    variant="outlined"
                    inputmode="decimal"
                    :rules="[
                      optionalDecimalRule,
                    ]"
                  />
                </v-col>

                <v-col
                  cols="12"
                  sm="6"
                  lg="3"
                >
                  <v-text-field
                    v-model="form
                      .informacao_nutricional
                      .carboidratos_g
                    "
                    label="Carboidratos"
                    suffix="g"
                    variant="outlined"
                    inputmode="decimal"
                    :rules="[
                      optionalDecimalRule,
                    ]"
                  />
                </v-col>

                <v-col
                  cols="12"
                  sm="6"
                  lg="3"
                >
                  <v-text-field
                    v-model="form
                      .informacao_nutricional
                      .proteinas_g
                    "
                    label="Proteínas"
                    suffix="g"
                    variant="outlined"
                    inputmode="decimal"
                    :rules="[
                      optionalDecimalRule,
                    ]"
                  />
                </v-col>

                <v-col
                  cols="12"
                  sm="6"
                  lg="3"
                >
                  <v-text-field
                    v-model="form
                      .informacao_nutricional
                      .gorduras_totais_g
                    "
                    label="Gorduras totais"
                    suffix="g"
                    variant="outlined"
                    inputmode="decimal"
                    :rules="[
                      optionalDecimalRule,
                    ]"
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="6"
                >
                  <v-textarea
                    v-model="form
                      .informacao_nutricional
                      .ingredientes
                    "
                    label="Ingredientes"
                    variant="outlined"
                    rows="3"
                    auto-grow
                  />
                </v-col>

                <v-col
                  cols="12"
                  md="6"
                >
                  <v-textarea
                    v-model="form
                      .informacao_nutricional
                      .alergenicos
                    "
                    label="Alergênicos"
                    variant="outlined"
                    rows="3"
                    auto-grow
                  />
                </v-col>
              </v-row>
            </div>
          </v-expand-transition>
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

    <v-dialog
      v-model="categoriaDialog"
      max-width="500"
      :persistent="savingCategoria"
    >
      <v-card rounded="xl">
        <v-form
          ref="categoriaFormRef"
          @submit.prevent="createCategoria"
        >
          <v-card-title class="pa-6 pb-2">
            Nova categoria
          </v-card-title>

          <v-card-subtitle class="px-6">
            Cadastre uma nova categoria para os produtos.
          </v-card-subtitle>

          <v-card-text class="pa-6">
            <v-alert
              v-if="categoriaErrorMessage"
              type="error"
              variant="tonal"
              class="mb-5"
            >
              {{ categoriaErrorMessage }}
            </v-alert>

            <v-text-field
              v-model="categoriaForm.nome"
              label="Nome"
              variant="outlined"
              maxlength="30"
              autofocus
              :disabled="savingCategoria"
              :rules="[categoryNameRule]"
              required
            />
          </v-card-text>

          <v-card-actions class="px-6 pb-6">
            <v-spacer />

            <v-btn
              variant="text"
              :disabled="savingCategoria"
              @click="closeCategoriaDialog"
            >
              Cancelar
            </v-btn>

            <v-btn
              type="submit"
              prepend-icon="mdi-plus"
              :loading="savingCategoria"
              :disabled="savingCategoria"
            >
              Cadastrar
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="unidadeDialog"
      max-width="550"
      :persistent="savingUnidade"
    >
      <v-card rounded="xl">
        <v-form
          ref="unidadeFormRef"
          @submit.prevent="createUnidadeMedida"
        >
          <v-card-title class="pa-6 pb-2">
            Nova unidade de medida
          </v-card-title>

          <v-card-subtitle class="px-6">
            Cadastre uma unidade para utilização
            nos produtos e informações nutricionais.
          </v-card-subtitle>

          <v-card-text class="pa-6">
            <v-alert
              v-if="unidadeErrorMessage"
              type="error"
              variant="tonal"
              class="mb-5"
            >
              {{ unidadeErrorMessage }}
            </v-alert>

            <v-row>
              <v-col
                cols="12"
                sm="8"
              >
                <v-text-field
                  v-model="unidadeForm.nome"
                  label="Nome"
                  variant="outlined"
                  maxlength="30"
                  autofocus
                  :disabled="savingUnidade"
                  :rules="[unitNameRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                sm="4"
              >
                <v-text-field
                  v-model="unidadeForm.sigla"
                  label="Sigla"
                  variant="outlined"
                  maxlength="5"
                  :disabled="savingUnidade"
                  :rules="[unitSiglaRule]"
                  required
                />
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions class="px-6 pb-6">
            <v-spacer />

            <v-btn
              variant="text"
              :disabled="savingUnidade"
              @click="closeUnidadeDialog"
            >
              Cancelar
            </v-btn>

            <v-btn
              type="submit"
              prepend-icon="mdi-plus"
              :loading="savingUnidade"
              :disabled="savingUnidade"
            >
              Cadastrar
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.field-with-action {
  display: flex;
  gap: 8px;
  align-items: flex-start;
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