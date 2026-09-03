export type DataTableAlign = 
    | 'start'
    | 'center'
    | 'end'

export interface DataTableHeader {
    key: string
    title: string
    align?: DataTableAlign
    width?: string
}

export interface DataTableAction {
    key: string
    title: string
    icon: string
    disabled?: boolean | ((item: Record<string, unknown>) => boolean)
}

export interface DataTableActionEvent<T = Record<string, unknown>> {
    action: string
    item: T
}