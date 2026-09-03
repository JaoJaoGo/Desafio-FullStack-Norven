<script lang="ts">
import { defineComponent, type PropType } from 'vue'
import type { DataTableAction, DataTableHeader } from '@/types/dataTable'

export default defineComponent({
    name: "AppDataTable",

    props: {
        headers: {
            type: Array as PropType<DataTableHeader[]>,
            required: true,
        },

        items: {
            type: Array as PropType<Record<string, unknown>[]>,
            required: true,
        },

        actions: {
            type: Array as PropType<DataTableAction[]>,
            default: () => [],
        },

        loading: {
            type: Boolean,
            default: false,
        },

        page: {
            type: Number,
            required: true,
        },

        perPage: {
            type: Number,
            required: true,
        },

        totalItems: {
            type: Number,
            required: true,
        },

        itemKey: {
            type: String,
            default: 'id',
        },

        emptyText: {
            type: String,
            default: 'Nenhum registro encontrado.',
        },

        perPageOptions: {
            type: Array as PropType<number[]>,
            default: () => [
                10,
                20,
                50,
                100,
            ],
        },
    },

    emits: [
        'update:page',
        'update:perPage',
        'action',
    ],

    data () {
        return {
            contextMenu: {
                visible: false,
                x: 0,
                y: 0,
                item: null as Record<string, unknown> | null,
            },
        }
    },

    computed: {
        totalPages(): number {
            if (this.totalItems === 0) {
                return 0
            }

            return Math.ceil(this.totalItems / this.perPage)
        },

        startItem(): number {
            if (this.totalItems === 0) {
                return 0
            }

            return (this.page - 1) * this.perPage + 1
        },

        endItem(): number {
            if (this.totalItems === 0) {
                return 0
            }

            return Math.min(this.page * this.perPage, this.totalItems)
        },

        columnCount(): number {
            return this.headers.length + (this.actions.length > 0 ? 1 : 0)
        },

        contextMenuStyle(): Record<string, string> {
            return {
                left: `${this.contextMenu.x}px`,
                top: `${this.contextMenu.y}px`,
            }
        },
    },

    mounted() {
        document.addEventListener('click', this.closeContextMenu)
        window.addEventListener('resize', this.closeContextMenu)
        window.addEventListener('scroll', this.closeContextMenu, true)
    },

    beforeUnmount() {
        document.removeEventListener('click', this.closeContextMenu)
        window.removeEventListener('resize', this.closeContextMenu)
        window.removeEventListener('scroll', this.closeContextMenu, true)
    },

    methods: {
        getValue(item: Record<string, unknown>, key: string): unknown {
            return item[key]
        },

        getItemKey(item: Record<string, unknown>, index: number): string | number {
            const value = item[this.itemKey]

            if (typeof value === 'string' || typeof value === 'number') {
                return value
            }

            return index
        },

        getAlignClass(
            align:
                | 'start'
                | 'center'
                | 'end' = 'start'
        ): string {
            return `text-${align}`
        },

        openContextMenu(event: MouseEvent, item: Record<string, unknown>): void {
            const menuWidth = 220
            const menuHeight = this.actions.length * 48 + 16

            const maxX = window.innerWidth - menuWidth - 8
            const maxY = window.innerHeight - menuHeight - 8

            this.contextMenu = {
                visible: true,

                x: Math.max(8, Math.min(event.clientX, maxX)),
                y: Math.max(8, Math.min(event.clientY, maxY)),
                
                item,
            }
        },

        closeContextMenu(): void {
            this.contextMenu.visible = false

            this.contextMenu.item = null
        },

        emitAction(action: DataTableAction, item: Record<string, unknown>): void {
            if (this.isActionDisabled(action, item)) {
                return
            }

            this.$emit(
                'action',
                {
                    action: action.key,
                    item,
                },
            )

            this.closeContextMenu()
        },

        emitContextAction(action: DataTableAction): void {
            if (!this.contextMenu.item) {
                return
            }

            this.emitAction(action, this.contextMenu.item)
        },

        updatePage(value: number): void {
            this.$emit('update:page', value)
        },

        updatePerPage(value: number | null): void {
            if (!value) {
                return
            }

            this.$emit('update:perPage', Number(value))
        },

        isActionDisabled(
          action: DataTableAction,
          item: Record<
            string,
            unknown
          >,
        ): boolean {
          if (
            typeof action.disabled
            === 'function'
          ) {
            return action.disabled(
              item,
            )
          }

          return Boolean(
            action.disabled,
          )
        },
    },
})
</script>

<template>
  <v-card
    rounded="xl"
    variant="outlined"
    class="data-table-card"
  >
    <v-progress-linear
      v-if="loading"
      indeterminate
    />

    <v-table class="data-table">
      <thead>
        <tr>
          <th
            v-for="header in headers"
            :key="header.key"
            :class="getAlignClass(header.align)"
            :style="{width: header.width}"
          >
            {{ header.title }}
          </th>

          <th
            v-if="actions.length > 0"
            class="text-end"
            style="width: 120px"
          >
            Ações
          </th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="(item, index) in items"
          :key="getItemKey(item, index)"
          class="data-row"
          @contextmenu.prevent="openContextMenu($event, item)"
        >
          <td
            v-for="header in headers"
            :key="header.key"
            :class="getAlignClass(header.align)"
          >
            <slot
              :name="`item-${header.key}`"
              :item="item"
              :value="getValue(item, header.key)"
            >
              {{ getValue(item, header.key) }}
            </slot>
          </td>

          <td v-if="actions.length > 0">
            <div class="d-flex justify-end ga-1">
              <v-btn
                v-for="action in actions"
                :key="action.key"
                :icon="action.icon"
                :title="action.title"
                :disabled="isActionDisabled(action, item)"
                size="small"
                variant="text"
                @click.stop="emitAction(action, item)"
              />
            </div>
          </td>
        </tr>

        <tr v-if="!loading && items.length === 0">
          <td
            :colspan="columnCount"
            class="empty-state"
          >
            <v-icon
              icon="mdi-database-search-outline"
              size="38"
              class="mb-3"
            />

            <div class="text-body-1 font-weight-medium">
              {{ emptyText }}
            </div>
          </td>
        </tr>
      </tbody>
    </v-table>

    <v-divider />

    <div class="data-table-footer">
      <div class="text-body-2 text-medium-emphasis">
        {{ startItem }}–{{ endItem }}
        de
        {{ totalItems }}
        registros
      </div>

      <div class="d-flex align-center ga-4">
        <div class="d-flex align-center ga-2">
          <span class="text-body-2 text-medium-emphasis">
            Por página
          </span>

          <v-select
            :model-value="perPage"
            :items="perPageOptions"
            density="compact"
            variant="outlined"
            hide-details
            class="per-page-select"
            @update:model-value="updatePerPage"
          />
        </div>

        <v-pagination
          v-if="totalPages > 1"
          :model-value="page"
          :length="totalPages"
          :total-visible="5"
          density="comfortable"
          @update:model-value="updatePage"
        />
      </div>
    </div>
  </v-card>

  <div
    v-if="contextMenu.visible"
    class="context-menu"
    :style="contextMenuStyle"
    @contextmenu.prevent
    @click.stop
  >
    <v-card
      min-width="210"
      rounded="lg"
      elevation="10"
    >
      <v-list
        nav
        density="comfortable"
      >
        <v-list-item
          v-for="action in actions"
          :key="action.key"
          :title="action.title"
          :prepend-icon="action.icon"
          :disabled="contextMenu.item ? isActionDisabled(action, contextMenu.item) : true"
          @click="emitContextAction(action)"
        />
      </v-list>
    </v-card>
  </div>
</template>

<style scoped>
.data-table-card {
  overflow: hidden;
}

.data-table th {
  white-space: nowrap;
  font-weight: 600;
}

.data-row {
  cursor: context-menu;
}

.data-row:hover {
  background:
    rgba(
      var(--v-theme-on-surface),
      0.035
    );
}

.empty-state {
  padding: 48px 24px !important;
  text-align: center;
  color:
    rgba(
      var(--v-theme-on-surface),
      0.6
    );
}

.data-table-footer {
  display: flex;
  gap: 24px;
  align-items: center;
  justify-content:
    space-between;
  padding: 16px 20px;
}

.per-page-select {
  width: 90px;
}

.context-menu {
  position: fixed;
  z-index: 3000;
}

@media (max-width: 700px) {
  .data-table-footer {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>