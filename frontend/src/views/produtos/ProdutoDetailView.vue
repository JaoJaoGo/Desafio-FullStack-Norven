<script lang="ts">
import { defineComponent } from 'vue'

import AppDataTable from '@/components/AppDataTable.vue'
import { ApiError } from '@/services/api'
import { estoqueService } from '@/services/estoqueService'
import { fornecedorService } from '@/services/fornecedorService'
import { loteService } from '@/services/loteService'
import { movimentacaoService } from '@/services/movimentacaoService'
import { produtoService } from '@/services/produtoService'

import type { DataTableHeader } from '@/types/dataTable'
import type { Estoque } from '@/types/estoque'
import type { Fornecedor } from '@/types/fornecedor'
import type { Lote } from '@/types/lote'
import type { Entrada, EntradaCreatePayload, Saida, SaidaCreatePayload, TipoMovimentacao, TipoSaida } from '@/types/movimentacao'
import type { ProdutoDetail, ProdutoStatus } from '@/types/produto'

interface FormReference {
    validate: () => Promise<{ valid: boolean }>
}

export default defineComponent({
    name: 'ProdutoDetailView',

    components: {
        AppDataTable,
    },

    data() {
        return {
            produto: null as ProdutoDetail | null,

            loading: false,
            errorMessage: '',

            lotes: [] as Lote[],
            todosLotes: [] as Lote[],

            lotePage: 1,
            lotePerPage: 10,
            loteTotal: 0,
            loadingLotes: false,

            entradas: [] as Entrada[],
            entradaPage: 1,
            entradaPerPage: 10,
            entradaTotal: 0,
            loadingEntradas: false,

            saidas: [] as Saida[],
            saidaPage: 1,
            saidaPerPage: 10,
            saidaTotal: 0,
            loadingSaidas: false,

            estoquesComSaldo: [] as Estoque[],

            fornecedores: [] as Fornecedor[],

            loteHeaders: [
                {
                    key: 'numero',
                    title: 'Número',
                },
                {
                    key: 'data_validade',
                    title: 'Data de validade',
                },
            ] as DataTableHeader[],

            entradaHeaders: [
                {
                    key: 'data_entrada',
                    title: 'Data',
                },
                {
                    key: 'lote_numero',
                    title: 'Lote',
                },
                {
                    key: 'fornecedor_nome',
                    title: 'Fornecedor',
                },
                {
                    key: 'quantidade',
                    title: 'Quantidade',
                },
                {
                    key: 'preco_custo_unitario',
                    title: 'Custo unitário',
                },
                {
                    key: 'tipo_entrada',
                    title: 'Tipo',
                },
                {
                    key: 'usuario_nome',
                    title: 'Responsável',
                },
                {
                    key: 'localizacao',
                    title: 'Localização',
                },
            ] as DataTableHeader[],

            saidaHeaders: [
                {
                    key: 'data_saida',
                    title: 'Data',
                },
                {
                    key: 'lote_numero',
                    title: 'Lote',
                },
                {
                    key: 'quantidade',
                    title: 'Quantidade',
                },
                {
                    key: 'tipo_saida',
                    title: 'Tipo',
                },
                {
                    key: 'preco_venda_unitario',
                    title: 'Preço',
                },
                {
                    key: 'usuario_nome',
                    title: 'Responsável',
                },
            ] as DataTableHeader[],

            loteDialog: false,
            savingLote: false,
            loteErrorMessage: '',

            loteForm: {
                numero: '',
                data_validade: '',
            },

            movimentacaoDialog: false,
            savingMovimentacao: false,
            movimentacaoErrorMessage: '',

            tipoMovimentacao: null as TipoMovimentacao | null,

            entradaForm: {
                fornecedor_id: null as number | null,
                lote_id: null as number | null,
                quantidade: '',
                preco_custo_unitario: '',
                tipo_entrada: '',
                observacao: '',
                data_entrada: '',
                corredor: '',
                prateleira: '',
                secao: '',
            },

            saidaForm: {
                estoque_id: null as number | null,
                quantidade: '',
                tipo_saida: null as TipoSaida | null,
                preco_venda_unitario: '',
                data_saida: '',
            },

            tipoSaidaOptions: [
                {
                    title: 'Venda',
                    value: 'VENDA',
                },
                {
                    title: 'Perda',
                    value: 'PERDA',
                },
                {
                    title: 'Avaria',
                    value: 'AVARIA',
                },
                {
                    title: 'Vencimento',
                    value: 'VENCIMENTO',
                },
                {
                    title: 'Recall',
                    value: 'RECALL',
                },
            ],
        }
    },

    computed: {
        produtoId(): number | null {
            const id = Number(this.$route.params.id)

            if (!Number.isInteger(id) || id <= 0) {
                return null
            }

            return id
        },

        possuiLotes(): boolean {
            return this.loteTotal > 0
        },

        possuiEstoque(): boolean {
            return Number(this.produto?.estoque_total ?? 0) > 0
        },

        localizacoesAtuais(): Estoque[] {
            if (!this.produto) {
                return []
            }

            return this.produto.estoques.filter((estoque) => Number(estoque.quantidade_atual) > 0)
        },

        loteOptions() {
            return this.todosLotes.map(
                (lote) => ({
                    title: lote.data_validade ? (`${lote.numero} - ` + this.formatDate(lote.data_validade)) : lote.numero,
                    value: lote.id,
                }),
            )
        },

        fornecedorOptions() {
            return this.fornecedores.map(
                (fornecedor) => ({
                    title: fornecedor.nome,
                    value: fornecedor.id,
                }),
            )
        },

        estoqueOptions() {
            return this.estoquesComSaldo
                .map(
                    (estoque) => ({
                        title: (
                            `Lote ${estoque.lote_numero}` + ` • ${estoque.corredor}` + ` / ${estoque.prateleira}` + ` / ${estoque.secao}` +
                            ` • ${this.formatQuantidade(estoque.quantidade_atual)}`
                        ),

                        value: estoque.id,
                    }),
                )
        },

        isVenda(): boolean {
            return this.saidaForm.tipo_saida === 'VENDA'
        },
    },

    mounted() {
        void this.initialize()
    },

    methods: {
        async initialize(): Promise<void> {
            const produtoId = this.produtoId

            if (!produtoId) {
                await this.$router.replace({ name: 'produtos' })

                return
            }

            this.loading = true
            this.errorMessage = ''

            try {
                await this.loadProduto()

                await Promise.all([
                    this.loadLotes(),
                    this.loadTodosLotes(),
                    this.loadEstoquesComSaldo(),
                ])

                if (this.possuiLotes) {
                    await Promise.all([
                        this.loadEntradas(),
                        this.loadSaidas(),
                    ])
                }
            } catch (error: unknown) {
                this.handleError(error, 'Não foi possível carregar o produto.')
            } finally {
                this.loading = false
            }
        },

        async loadProduto(): Promise<void> {
            const produtoId = this.produtoId

            if (!produtoId) {
                return
            }

            this.produto = await produtoService.findById(produtoId)
        },

        async loadLotes(): Promise<void> {
            const produtoId = this.produtoId

            if (!produtoId) {
                return
            }

            this.loadingLotes = true

            try {
                const response = await loteService.listByProduct(
                    produtoId,
                    this.lotePage,
                    this.lotePerPage,
                )

                this.lotes = response.items

                this.loteTotal = response.total
            } finally {
                this.loadingLotes = false
            }
        },

        async loadTodosLotes(): Promise<void> {
            const produtoId = this.produtoId

            if (!produtoId) {
                return
            }

            this.todosLotes = await loteService.listAllByProduct(produtoId)
        },

        async loadEntradas(): Promise<void> {
            const produtoId = this.produtoId

            if (!produtoId) {
                return
            }

            this.loadingEntradas = true

            try {
                const response = await movimentacaoService.listEntradas(
                    produtoId,
                    this.entradaPage,
                    this.entradaPerPage,
                )

                this.entradas = response.items

                this.entradaTotal = response.total
            } finally {
                this.loadingEntradas = false
            }
        },

        async loadSaidas(): Promise<void> {
            const produtoId = this.produtoId

            if (!produtoId) {
                return
            }

            this.loadingSaidas = true

            try {
                const response = await movimentacaoService.listSaidas(
                    produtoId,
                    this.saidaPage,
                    this.saidaPerPage,
                )

                this.saidas = response.items

                this.saidaTotal = response.total
            } finally {
                this.loadingSaidas = false
            }
        },

        async loadEstoquesComSaldo(): Promise<void> {
            const produtoId = this.produtoId

            if (!produtoId) {
                return
            }

            this.estoquesComSaldo = await estoqueService.listAllByProduct(
                produtoId,
                true,
            )
        },

        async loadFornecedores(): Promise<void> {
            const items: Fornecedor[] = []

            let page = 1

            while (true) {
                const response = await fornecedorService.list({
                    page,
                    perPage: 100,
                })

                items.push(...response.items)

                if (items.length >= response.total || response.items.length === 0) {
                    break
                }

                page += 1
            }

            this.fornecedores = items.sort((first, second) => first.nome.localeCompare(second.nome, 'pt-BR'))
        },

        async refreshAfterLote(): Promise<void> {
            await Promise.all([
                this.loadProduto(),
                this.loadLotes(),
                this.loadTodosLotes(),
            ])
        },

        async refreshAfterMovimentacao(): Promise<void> {
            await Promise.all([
                this.loadProduto(),
                this.loadEntradas(),
                this.loadSaidas(),
                this.loadEstoquesComSaldo(),
            ])
        },

        formatCurrency(value: unknown): string {
            const numeric = Number(value)

            if (!Number.isFinite(numeric)) {
                return '-'
            }

            return new Intl.NumberFormat(
                'pt-BR',
                {
                    style: 'currency',
                    currency: 'BRL',
                },
            ).format(numeric)
        },

        formatQuantidade(value: unknown): string {
            const numeric = Number(value)

            if (!Number.isFinite(numeric)) {
                return '-'
            }

            return new Intl.NumberFormat(
                'pt-BR',
                {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 3,
                },
            ).format(numeric)
        },

        formatEstoque(): string {
            if (!this.produto || !this.possuiEstoque) {
                return 'Sem estoque'
            }

            return `${this.formatQuantidade(this.produto.estoque_total)} ` + this.produto.unidade_medida.sigla
        },

        formatDate(value: unknown): string {
            if (!value) {
                return '-'
            }

            const raw = String(value)

            const datePart = raw.split('T')[0] ?? ''

            const parts = datePart.split('-')

            if (parts.length !== 3) {
                return raw
            }

            return `${parts[2]}/${parts[1]}/${parts[0]}`
        },

        formatDateTime(value: unknown): string {
            if (!value) {
                return '-'
            }

            const date = new Date(String(value))

            if (Number.isNaN(date.getTime())) {
                return String(value)
            }

            return new Intl.DateTimeFormat(
                'pt-BR',
                {
                    dateStyle: 'short',
                    timeStyle: 'short',
                },
            ).format(date)
        },

        formatStatus(status: ProdutoStatus): string {
            const labels: Record<ProdutoStatus, string> = {
                SEM_ESTOQUE: 'Sem estoque',
                VENCIDO: 'Vencido',
                PROXIMO_VENCIMENTO: 'Próximo do vencimento',
                ESTOQUE_BAIXO: 'Estoque baixo',
                OK: 'OK',
            }

            return labels[status]
        },

        statusColor(status: ProdutoStatus): string {
            const colors: Record<ProdutoStatus, string> = {
                SEM_ESTOQUE: 'secondary',
                VENCIDO: 'error',
                PROXIMO_VENCIMENTO: 'warning',
                ESTOQUE_BAIXO: 'warning',
                OK: 'success',
            }

            return colors[status]
        },

        requiredRule(value: unknown): true | string {
            if (value === null || value === undefined || String(value).trim() === '') {
                return 'Campo obrigatório.'
            }

            return true
        },

        positiveQuantityRule(value: unknown): true | string {
            const normalized = String(value ?? '').trim().replace(',', '.')

            if (!/^\d+(\.\d{1,3})?$/.test(normalized) || Number(normalized) <= 0) {
                return 'Informe uma quantidade maior que zero com até 3 casas decimais.'
            }

            return true
        },

        moneyRule(value: unknown): true | string {
            const normalized = String(value ?? '').trim().replace(',', '.')

            if (!/^\d+(\.\d{1,2})?$/.test(normalized) || Number(normalized) < 0) {
                return 'Informe um valor válido com até 2 casas decimais.'
            }

            return true
        },

        optionalMoneyRule(value: unknown): true | string {
            if (value === null || value === undefined || String(value).trim() === '') {
                return true
            }

            return this.moneyRule(value)
        },

        normalizeDecimal(value: string): string {
            return value.trim().replace(',', '.')
        },

        openLoteDialog(): void {
            this.loteForm = {
                numero: '',
                data_validade: '',
            }

            this.loteErrorMessage = ''
            this.loteDialog = true
        },

        async saveLote(): Promise<void> {
            const form = this.$refs.loteFormRef as FormReference | undefined

            const produtoId = this.produtoId

            if (!form || !produtoId || !this.produto) {
                return
            }

            const validation = await form.validate()

            if (!validation.valid) {
                return
            }

            if (this.produto.eh_perecivel && !this.loteForm.data_validade) {
                this.loteErrorMessage = 'A data de validade é obrigatória para produtos perecíveis.'

                return
            }

            this.savingLote = true
            this.loteErrorMessage = ''

            try {
                await loteService.create({
                    numero: this.loteForm.numero.trim(),
                    data_validade: this.loteForm.data_validade || null,
                    produto_id: produtoId,
                })

                this.loteDialog = false

                await this.refreshAfterLote()
            } catch (error: unknown) {
                if (error instanceof ApiError) {
                    this.loteErrorMessage = error.message
                } else {
                    this.loteErrorMessage = 'Não foi possível cadastrar o lote.'
                }
            } finally {
                this.savingLote = false
            }
        },

        async openMovimentacaoDialog(): Promise<void> {
            if (!this.possuiLotes) {
                return
            }

            this.tipoMovimentacao = null

            this.entradaForm = {
                fornecedor_id: null,
                lote_id: null,
                quantidade: '',
                preco_custo_unitario: '',
                tipo_entrada: '',
                observacao: '',
                data_entrada: '',
                corredor: '',
                prateleira: '',
                secao: '',
            }

            this.saidaForm = {
                estoque_id: null,
                quantidade: '',
                tipo_saida: null,
                preco_venda_unitario: '',
                data_saida: '',
            }

            this.movimentacaoErrorMessage = ''

            try {
                await Promise.all([
                    this.loadTodosLotes(),
                    this.loadEstoquesComSaldo(),
                    this.loadFornecedores(),
                ])

                this.movimentacaoDialog = true
            } catch (error: unknown) {
                this.handleError(error, 'Não foi possível preparar o cadastro da movimentação.')
            }
        },

        async saveMovimentacao(): Promise<void> {
            if (this.tipoMovimentacao === 'ENTRADA') {
                await this.saveEntrada()
                return
            }

            if (this.tipoMovimentacao === 'SAIDA') {
                await this.saveSaida()
            }
        },

        async saveEntrada(): Promise<void> {
            const form = this.$refs.movimentacaoFormRef as FormReference | undefined

            const produtoId = this.produtoId

            if (!form || !produtoId) {
                return
            }

            const validation = await form.validate()

            if (!validation.valid) {
                return
            }

            this.savingMovimentacao = true
            this.movimentacaoErrorMessage = ''

            try {
                const payload: EntradaCreatePayload = {
                    fornecedor_id: Number(this.entradaForm.fornecedor_id),
                    lote_id: Number(this.entradaForm.lote_id),
                    quantidade: this.normalizeDecimal(this.entradaForm.quantidade),
                    preco_custo_unitario: this.normalizeDecimal(this.entradaForm.preco_custo_unitario),
                    tipo_entrada: this.entradaForm.tipo_entrada.trim(),
                    observacao: this.entradaForm.observacao.trim() || null,

                    localizacao: {
                        corredor: this.entradaForm.corredor.trim(),
                        prateleira: this.entradaForm.prateleira.trim(),
                        secao: this.entradaForm.secao.trim(),
                    },
                }

                if (this.entradaForm.data_entrada) {
                    payload.data_entrada = this.entradaForm.data_entrada
                }

                await movimentacaoService.createEntrada(produtoId, payload)

                this.movimentacaoDialog = false

                await this.refreshAfterMovimentacao()
            } catch (error: unknown) {
                if (error instanceof ApiError) {
                    this.movimentacaoErrorMessage = error.message
                } else {
                    this.movimentacaoErrorMessage = 'Não foi possível registrar a entrada.'
                }
            } finally {
                this.savingMovimentacao = false
            }
        },

        async saveSaida(): Promise<void> {
            const form = this.$refs.movimentacaoFormRef as FormReference | undefined

            const produtoId = this.produtoId

            if (!form || !produtoId) {
                return
            }

            const validation = await form.validate()

            if (!validation.valid) {
                return
            }

            this.savingMovimentacao = true
            this.movimentacaoErrorMessage = ''

            try {
                const payload: SaidaCreatePayload = {
                    estoque_id: Number(this.saidaForm.estoque_id),
                    quantidade: this.normalizeDecimal(this.saidaForm.quantidade),
                    tipo_saida: this.saidaForm.tipo_saida as TipoSaida,
                    preco_venda_unitario: this.isVenda && this.saidaForm.preco_venda_unitario.trim() ? this.normalizeDecimal(this.saidaForm.preco_venda_unitario) : null,
                }

                if (this.saidaForm.data_saida) {
                    payload.data_saida = this.saidaForm.data_saida
                }

                await movimentacaoService.createSaida(produtoId, payload)

                this.movimentacaoDialog = false

                await this.refreshAfterMovimentacao()
            } catch (error: unknown) {
                if (error instanceof ApiError) {
                    this.movimentacaoErrorMessage = error.message
                } else {
                    this.movimentacaoErrorMessage = 'Não foi possível registrar a saída.'
                }
            } finally {
                this.savingMovimentacao = false
            }
        },

        changeLotePage(page: number): void {
            this.lotePage = page
            void this.loadLotes()
        },

        changeLotePerPage(perPage: number): void {
            this.lotePage = 1
            this.lotePerPage = perPage
            void this.loadLotes()
        },

        changeEntradaPage(page: number): void {
            this.entradaPage = page
            void this.loadEntradas()
        },

        changeEntradaPerPage(perPage: number): void {
            this.entradaPage = 1
            this.entradaPerPage = perPage
            void this.loadEntradas()
        },

        changeSaidaPage(page: number): void {
            this.saidaPage = page
            void this.loadSaidas()
        },

        changeSaidaPerPage(perPage: number): void {
            this.saidaPage = 1
            this.saidaPerPage = perPage
            void this.loadSaidas()
        },

        handleError(error: unknown, fallback: string): void {
            if (error instanceof ApiError) {
                this.errorMessage = error.message
            } else {
                this.errorMessage = fallback
            }
        },

        async goBack(): Promise<void> {
            await this.$router.push({
                name: 'produtos',
            })
        },

        async editProduto(): Promise<void> {
            if (!this.produtoId) {
                return
            }

            await this.$router.push({
                name: 'produto-edit',

                params: {
                    id: this.produtoId,
                },
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
          @click="goBack"
        />

        <div>
          <h1 class="text-h4 font-weight-bold">
            {{ produto?.nome || 'Produto' }}
          </h1>

          <p class="text-body-1 text-medium-emphasis mt-2">
            Visualize os dados e gerencie o estoque
            deste produto.
          </p>
        </div>
      </div>

      <v-btn
        prepend-icon="mdi-pencil-outline"
        variant="tonal"
        :disabled="!produto"
        @click="editProduto"
      >
        Editar produto
      </v-btn>
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
    />

    <template v-else-if="produto">
      <v-card
        rounded="xl"
        variant="outlined"
        class="mb-6"
      >
        <v-card-title class="pa-6 pb-2">
          Dados do produto
        </v-card-title>

        <v-card-text class="pa-6">
          <v-row>
            <v-col
              cols="12"
              sm="6"
              lg="3"
            >
              <div class="detail-label">
                Código
              </div>

              <div class="detail-value">
                {{ produto.cod_idt }}
              </div>
            </v-col>

            <v-col
              cols="12"
              sm="6"
              lg="3"
            >
              <div class="detail-label">
                Categoria
              </div>

              <div class="detail-value">
                {{ produto.categoria.nome }}
              </div>
            </v-col>

            <v-col
              cols="12"
              sm="6"
              lg="3"
            >
              <div class="detail-label">
                Unidade de medida
              </div>

              <div class="detail-value">
                {{ produto.unidade_medida.nome }}
                ({{ produto.unidade_medida.sigla }})
              </div>
            </v-col>

            <v-col
              cols="12"
              sm="6"
              lg="3"
            >
              <div class="detail-label">
                Preço de venda
              </div>

              <div class="detail-value">
                {{
                  formatCurrency(
                    produto.preco_venda_atual,
                  )
                }}
              </div>
            </v-col>

            <v-col
              cols="12"
              sm="6"
              lg="3"
            >
              <div class="detail-label">
                Perecível
              </div>

              <div class="detail-value">
                {{
                  produto.eh_perecivel
                    ? 'Sim'
                    : 'Não'
                }}
              </div>
            </v-col>

            <v-col
              cols="12"
              sm="6"
              lg="4"
            >
              <div class="detail-label">
                Responsável pelo cadastro
              </div>

              <div class="detail-value">
                {{ produto.responsavel.nome }}

                <span class="text-medium-emphasis">
                  ({{ produto.responsavel.email }})
                </span>
              </div>
            </v-col>

            <v-col
              cols="12"
              sm="6"
              lg="3"
            >
              <div class="detail-label">
                Data de cadastro
              </div>

              <div class="detail-value">
                {{
                  formatDateTime(
                    produto.data_cadastro,
                  )
                }}
              </div>
            </v-col>

            <v-col cols="12">
              <div class="detail-label">
                Descrição
              </div>

              <div class="detail-value">
                {{ produto.descricao || '-' }}
              </div>
            </v-col>

            <v-col cols="12">
              <div class="detail-label mb-2">
                Status
              </div>

              <div class="d-flex flex-wrap ga-2">
                <v-chip
                  v-for="statusProduto in produto.statuses"
                  :key="statusProduto"
                  variant="tonal"
                  :color="statusColor(statusProduto)"
                >
                  {{ formatStatus(statusProduto) }}
                </v-chip>
              </div>
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
          Estoque
        </v-card-title>

        <v-card-text class="pa-6">
          <div class="stock-value mb-6">
            {{ formatEstoque() }}
          </div>

          <template v-if="localizacoesAtuais.length > 0">
            <div class="text-subtitle-1 font-weight-bold mb-3">
              Localizações
            </div>

            <v-row>
              <v-col
                v-for="estoque in localizacoesAtuais"
                :key="estoque.id"
                cols="12"
                md="6"
                lg="4"
              >
                <v-card
                  rounded="lg"
                  variant="tonal"
                >
                  <v-card-text>
                    <div class="font-weight-bold mb-2">
                      Lote {{ estoque.lote_numero }}
                    </div>

                    <div class="text-body-2">
                      Corredor:
                      {{ estoque.corredor }}
                    </div>

                    <div class="text-body-2">
                      Prateleira:
                      {{ estoque.prateleira }}
                    </div>

                    <div class="text-body-2">
                      Seção:
                      {{ estoque.secao }}
                    </div>

                    <div class="text-body-2 mt-2">
                      Saldo:
                      {{
                        formatQuantidade(
                          estoque.quantidade_atual,
                        )
                      }}
                      {{ produto.unidade_medida.sigla }}
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </template>
        </v-card-text>
      </v-card>

      <v-card
        rounded="xl"
        variant="outlined"
        class="mb-8"
      >
        <v-card-title class="pa-6 pb-2">
          Informação nutricional
        </v-card-title>

        <v-card-text class="pa-6">
          <template v-if="produto.informacao_nutricional">
            <v-row>
              <v-col
                cols="12"
                sm="6"
                lg="3"
              >
                <div class="detail-label">
                  Porção
                </div>

                <div class="detail-value">
                  {{
                    formatQuantidade(
                      produto
                        .informacao_nutricional
                        .porcao_quantidade,
                    )
                  }}

                  {{
                    produto
                      .informacao_nutricional
                      .unidade_porcao
                      .sigla
                  }}
                </div>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                lg="3"
              >
                <div class="detail-label">
                  Valor energético
                </div>

                <div class="detail-value">
                  {{
                    produto
                      .informacao_nutricional
                      .valor_energetico_kcal
                      ?? '-'
                  }}
                  kcal
                </div>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                lg="2"
              >
                <div class="detail-label">
                  Carboidratos
                </div>

                <div class="detail-value">
                  {{
                    produto
                      .informacao_nutricional
                      .carboidratos_g
                      ?? '-'
                  }}
                  g
                </div>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                lg="2"
              >
                <div class="detail-label">
                  Proteínas
                </div>

                <div class="detail-value">
                  {{
                    produto
                      .informacao_nutricional
                      .proteinas_g
                      ?? '-'
                  }}
                  g
                </div>
              </v-col>

              <v-col
                cols="12"
                sm="6"
                lg="2"
              >
                <div class="detail-label">
                  Gorduras totais
                </div>

                <div class="detail-value">
                  {{
                    produto
                      .informacao_nutricional
                      .gorduras_totais_g
                      ?? '-'
                  }}
                  g
                </div>
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <div class="detail-label">
                  Ingredientes
                </div>

                <div class="detail-value">
                  {{
                    produto
                      .informacao_nutricional
                      .ingredientes
                      || '-'
                  }}
                </div>
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <div class="detail-label">
                  Alergênicos
                </div>

                <div class="detail-value">
                  {{
                    produto
                      .informacao_nutricional
                      .alergenicos
                      || '-'
                  }}
                </div>
              </v-col>
            </v-row>
          </template>

          <div
            v-else
            class="text-medium-emphasis"
          >
            Nenhuma informação nutricional cadastrada.
          </div>
        </v-card-text>
      </v-card>

      <div class="section-header mb-4">
        <div>
          <h2 class="text-h5 font-weight-bold">
            Lotes
          </h2>

          <p class="text-body-2 text-medium-emphasis mt-1">
            Lotes vinculados exclusivamente a este produto.
          </p>
        </div>

        <v-btn
          prepend-icon="mdi-plus"
          @click="openLoteDialog"
        >
          Adicionar lote
        </v-btn>
      </div>

      <app-data-table
        :headers="loteHeaders"
        :items="lotes"
        :actions="[]"
        :loading="loadingLotes"
        :page="lotePage"
        :per-page="lotePerPage"
        :total-items="loteTotal"
        empty-text="Nenhum lote cadastrado para este produto."
        class="mb-8"
        @update:page="changeLotePage"
        @update:per-page="changeLotePerPage"
      >
        <template #item-data_validade="{ item }">
          {{
            formatDate(
              item.data_validade,
            )
          }}
        </template>
      </app-data-table>

      <v-alert
        v-if="!possuiLotes"
        type="info"
        variant="tonal"
        class="mb-8"
      >
        Cadastre ao menos um lote para habilitar
        as movimentações deste produto.
      </v-alert>

      <template v-if="possuiLotes">
        <div class="section-header mb-4">
          <div>
            <h2 class="text-h5 font-weight-bold">
              Movimentações
            </h2>

            <p class="text-body-2 text-medium-emphasis mt-1">
              Entradas e saídas registradas para este produto.
            </p>
          </div>

          <v-btn
            prepend-icon="mdi-swap-horizontal"
            @click="openMovimentacaoDialog"
          >
            Adicionar movimentação
          </v-btn>
        </div>

        <h3 class="text-h6 font-weight-bold mb-3">
          Entradas
        </h3>

        <app-data-table
          :headers="entradaHeaders"
          :items="entradas"
          :actions="[]"
          :loading="loadingEntradas"
          :page="entradaPage"
          :per-page="entradaPerPage"
          :total-items="entradaTotal"
          empty-text="Nenhuma entrada registrada."
          class="mb-8"
          @update:page="changeEntradaPage"
          @update:per-page="changeEntradaPerPage"
        >
          <template #item-data_entrada="{ item }">
            {{
              formatDateTime(
                item.data_entrada,
              )
            }}
          </template>

          <template #item-quantidade="{ item }">
            {{
              formatQuantidade(
                item.quantidade,
              )
            }}
            {{ produto.unidade_medida.sigla }}
          </template>

          <template #item-preco_custo_unitario="{ item }">
            {{
              formatCurrency(
                item.preco_custo_unitario,
              )
            }}
          </template>

          <template #item-localizacao="{ item }">
            {{
              `${item.corredor} / `
                + `${item.prateleira} / `
                + `${item.secao}`
            }}
          </template>
        </app-data-table>

        <h3 class="text-h6 font-weight-bold mb-3">
          Saídas
        </h3>

        <app-data-table
          :headers="saidaHeaders"
          :items="saidas"
          :actions="[]"
          :loading="loadingSaidas"
          :page="saidaPage"
          :per-page="saidaPerPage"
          :total-items="saidaTotal"
          empty-text="Nenhuma saída registrada."
          class="mb-8"
          @update:page="changeSaidaPage"
          @update:per-page="changeSaidaPerPage"
        >
          <template #item-data_saida="{ item }">
            {{
              formatDateTime(
                item.data_saida,
              )
            }}
          </template>

          <template #item-quantidade="{ item }">
            {{
              formatQuantidade(
                item.quantidade,
              )
            }}
            {{ produto.unidade_medida.sigla }}
          </template>

          <template #item-preco_venda_unitario="{ item }">
            {{
              item.preco_venda_unitario
                ? formatCurrency(
                  item.preco_venda_unitario,
                )
                : '-'
            }}
          </template>
        </app-data-table>
      </template>
    </template>

    <v-dialog
      v-model="loteDialog"
      max-width="520"
      :persistent="savingLote"
    >
      <v-card rounded="xl">
        <v-form
          ref="loteFormRef"
          @submit.prevent="saveLote"
        >
          <v-card-title class="pa-6 pb-2">
            Novo lote
          </v-card-title>

          <v-card-subtitle class="px-6">
            {{ produto?.nome }}
          </v-card-subtitle>

          <v-card-text class="pa-6">
            <v-alert
              v-if="loteErrorMessage"
              type="error"
              variant="tonal"
              class="mb-5"
            >
              {{ loteErrorMessage }}
            </v-alert>

            <v-text-field
              v-model="loteForm.numero"
              label="Número do lote"
              maxlength="30"
              variant="outlined"
              :rules="[requiredRule]"
              required
            />

            <v-text-field
              v-model="loteForm.data_validade"
              label="Data de validade"
              type="date"
              variant="outlined"
              :rules="produto?.eh_perecivel
                ? [requiredRule]
                : []
              "
              :required="produto?.eh_perecivel"
              :hint="produto?.eh_perecivel
                ? 'Obrigatória para produtos perecíveis.'
                : 'Opcional para produtos não perecíveis.'
              "
              persistent-hint
            />
          </v-card-text>

          <v-card-actions class="px-6 pb-6">
            <v-spacer />

            <v-btn
              variant="text"
              :disabled="savingLote"
              @click="loteDialog = false"
            >
              Cancelar
            </v-btn>

            <v-btn
              type="submit"
              :loading="savingLote"
              :disabled="savingLote"
            >
              Adicionar
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>

    <v-dialog
      v-model="movimentacaoDialog"
      max-width="760"
      :persistent="savingMovimentacao"
    >
      <v-card rounded="xl">
        <v-form
          ref="movimentacaoFormRef"
          @submit.prevent="saveMovimentacao"
        >
          <v-card-title class="pa-6 pb-2">
            Nova movimentação
          </v-card-title>

          <v-card-subtitle class="px-6">
            Selecione primeiro o tipo da movimentação.
          </v-card-subtitle>

          <v-card-text class="pa-6">
            <v-alert
              v-if="movimentacaoErrorMessage"
              type="error"
              variant="tonal"
              class="mb-5"
            >
              {{ movimentacaoErrorMessage }}
            </v-alert>

            <v-radio-group
              v-model="tipoMovimentacao"
              inline
              class="mb-5"
            >
              <v-radio
                label="Entrada"
                value="ENTRADA"
              />

              <v-radio
                label="Saída"
                value="SAIDA"
                :disabled="estoquesComSaldo.length === 0"
              />
            </v-radio-group>

            <v-alert
              v-if="estoquesComSaldo.length === 0"
              type="info"
              variant="tonal"
              density="compact"
              class="mb-5"
            >
              Não há saldo disponível. Apenas entradas
              podem ser registradas neste momento.
            </v-alert>

            <v-row v-if="tipoMovimentacao === 'ENTRADA'">
              <v-col
                cols="12"
                md="6"
              >
                <v-select
                  v-model="entradaForm.lote_id"
                  :items="loteOptions"
                  label="Lote"
                  variant="outlined"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <v-select
                  v-model="entradaForm.fornecedor_id"
                  :items="fornecedorOptions"
                  label="Fornecedor"
                  variant="outlined"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="entradaForm.quantidade"
                  label="Quantidade"
                  variant="outlined"
                  inputmode="decimal"
                  :suffix="produto?.unidade_medida.sigla"
                  :rules="[positiveQuantityRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="entradaForm.preco_custo_unitario"
                  label="Preço de custo unitário"
                  prefix="R$"
                  variant="outlined"
                  inputmode="decimal"
                  :rules="[moneyRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="entradaForm.tipo_entrada"
                  label="Tipo de entrada"
                  maxlength="30"
                  variant="outlined"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="entradaForm.data_entrada"
                  label="Data da entrada"
                  type="datetime-local"
                  variant="outlined"
                  hint="Opcional. Vazio utiliza a data atual."
                  persistent-hint
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="entradaForm.observacao"
                  label="Observação"
                  variant="outlined"
                  rows="2"
                  auto-grow
                />
              </v-col>

              <v-col cols="12">
                <div class="text-subtitle-1 font-weight-bold mb-4">
                  Localização no estoque
                </div>
              </v-col>

              <v-col
                cols="12"
                md="4"
              >
                <v-text-field
                  v-model="entradaForm.corredor"
                  label="Corredor"
                  maxlength="30"
                  variant="outlined"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                md="4"
              >
                <v-text-field
                  v-model="entradaForm.prateleira"
                  label="Prateleira"
                  maxlength="30"
                  variant="outlined"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                md="4"
              >
                <v-text-field
                  v-model="entradaForm.secao"
                  label="Seção"
                  maxlength="30"
                  variant="outlined"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>
            </v-row>

            <v-row v-if="tipoMovimentacao === 'SAIDA'">
              <v-col cols="12">
                <v-select
                  v-model="saidaForm.estoque_id"
                  :items="estoqueOptions"
                  label="Lote e localização de retirada"
                  variant="outlined"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="saidaForm.quantidade"
                  label="Quantidade"
                  variant="outlined"
                  inputmode="decimal"
                  :suffix="produto?.unidade_medida.sigla"
                  :rules="[positiveQuantityRule]"
                  required
                />
              </v-col>

              <v-col
                cols="12"
                md="6"
              >
                <v-select
                  v-model="saidaForm.tipo_saida"
                  :items="tipoSaidaOptions"
                  label="Tipo de saída"
                  variant="outlined"
                  :rules="[requiredRule]"
                  required
                />
              </v-col>

              <v-col
                v-if="isVenda"
                cols="12"
                md="6"
              >
                <v-text-field
                  v-model="saidaForm.preco_venda_unitario"
                  label="Preço de venda unitário"
                  prefix="R$"
                  variant="outlined"
                  inputmode="decimal"
                  :rules="[optionalMoneyRule]"
                  hint="Deixe vazio para usar o preço atual do produto."
                  persistent-hint
                />
              </v-col>

              <v-col
                cols="12"
                :md="isVenda ? 6 : 12"
              >
                <v-text-field
                  v-model="saidaForm.data_saida"
                  label="Data da saída"
                  type="datetime-local"
                  variant="outlined"
                  hint="Opcional. Vazio utiliza a data atual."
                  persistent-hint
                />
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions class="px-6 pb-6">
            <v-spacer />

            <v-btn
              variant="text"
              :disabled="savingMovimentacao"
              @click="movimentacaoDialog = false"
            >
              Cancelar
            </v-btn>

            <v-btn
              type="submit"
              :loading="savingMovimentacao"
              :disabled="savingMovimentacao
                || !tipoMovimentacao
              "
            >
              Salvar movimentação
            </v-btn>
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.page-header,
.section-header {
    display: flex;
    gap: 24px;
    align-items: center;
    justify-content: space-between;
}

.detail-label {
    margin-bottom: 4px;
    font-size: 0.78rem;
    color:
        rgba(var(--v-theme-on-surface),
            0.62);
}

.detail-value {
    font-weight: 500;
}

.stock-value {
    font-size: 2rem;
    font-weight: 700;
}

@media (max-width: 700px) {

    .page-header,
    .section-header {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>