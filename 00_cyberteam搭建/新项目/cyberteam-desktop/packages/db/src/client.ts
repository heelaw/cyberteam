import { existsSync, mkdirSync } from 'node:fs'
import { dirname } from 'node:path'
import { DatabaseSync } from 'node:sqlite'
import {
  schemaStatements,
  type SchemaTableName,
  type CompanyRow,
  type DepartmentRow,
  type AgentRow,
  type SkillRow,
  type ConversationRow,
  type MessageRow,
  type PlaygroundDocumentRow,
  type ReviewRecordRow,
  type RoadmapPhaseRow,
  type TemplateRow,
} from './schema'

type Row = Record<string, unknown>
type SqlValue = string | number | bigint | Uint8Array | null

function ensureDirectory(dbPath: string) {
  if (dbPath === ':memory:') {
    return
  }

  const dir = dirname(dbPath)
  if (!existsSync(dir)) {
    mkdirSync(dir, { recursive: true })
  }
}

function createDatabase(dbPath: string) {
  ensureDirectory(dbPath)
  const database = new DatabaseSync(dbPath)

  for (const statement of Object.values(schemaStatements)) {
    database.exec(statement)
  }

  return database
}

function serializeValue(value: unknown) {
  if (value === undefined || value === null) {
    return null
  }

  if (typeof value === 'boolean') {
    return value ? 1 : 0
  }

  if (Array.isArray(value) || typeof value === 'object') {
    return JSON.stringify(value)
  }

  return value as string | number | bigint
}

function quoteIdentifier(identifier: string) {
  return `"${identifier.split('"').join('""')}"`
}

function normalizeWhere(where: Partial<Row>) {
  const entries = Object.entries(where).filter(([, value]) => value !== undefined)
  if (entries.length === 0) {
    return { sql: '', values: [] as SqlValue[] }
  }

  return {
    sql: ` WHERE ${entries.map(([key]) => `${quoteIdentifier(key)} = ?`).join(' AND ')}`,
    values: entries.map(([, value]) => serializeValue(value) as SqlValue),
  }
}

export interface DbClient {
  database: DatabaseSync
  path: string
  query<T = Row>(table: SchemaTableName, where?: Partial<Row>): T[]
  get<T = Row>(table: SchemaTableName, where?: Partial<Row>): T | undefined
  insert<T extends object>(table: SchemaTableName, row: T): T
  update<T extends object>(table: SchemaTableName, where: Partial<Row>, patch: Partial<T>): number
  delete(table: SchemaTableName, where?: Partial<Row>): number
  close(): void
}

export function createDbClient(dbPath = ':memory:'): DbClient {
  const database = createDatabase(dbPath)

  return {
    database,
    path: dbPath,
    query<T = Row>(table: SchemaTableName, where: Partial<Row> = {}) {
      const normalized = normalizeWhere(where)
      const statement = database.prepare(`SELECT * FROM ${quoteIdentifier(table)}${normalized.sql}`)
      return statement.all(...normalized.values) as T[]
    },
    get<T = Row>(table: SchemaTableName, where: Partial<Row> = {}) {
      return this.query<T>(table, where)[0]
    },
    insert<T extends object>(table: SchemaTableName, row: T) {
      const entries = Object.entries(row as Record<string, unknown>)
      const columns = entries.map(([column]) => column)
      const values = entries.map(([, value]) => serializeValue(value) as SqlValue)
      const placeholders = columns.map(() => '?').join(', ')
      const statement = database.prepare(
        `INSERT OR REPLACE INTO ${quoteIdentifier(table)} (${columns.map(quoteIdentifier).join(', ')}) VALUES (${placeholders})`,
      )
      statement.run(...values)
      return row
    },
    update<T extends object>(table: SchemaTableName, where: Partial<Row>, patch: Partial<T>) {
      const assignments = Object.entries(patch as Record<string, unknown>).filter(([, value]) => value !== undefined)

      if (assignments.length === 0) {
        return 0
      }

      const normalized = normalizeWhere(where)
      const setClause = assignments.map(([column]) => `${quoteIdentifier(column)} = ?`).join(', ')
      const values = [
        ...assignments.map(([, value]) => serializeValue(value) as SqlValue),
        ...normalized.values,
      ]
      const statement = database.prepare(`UPDATE ${quoteIdentifier(table)} SET ${setClause}${normalized.sql}`)
      const result = statement.run(...values)
      return Number(result.changes ?? 0)
    },
    delete(table: SchemaTableName, where: Partial<Row> = {}) {
      const normalized = normalizeWhere(where)
      const statement = database.prepare(`DELETE FROM ${quoteIdentifier(table)}${normalized.sql}`)
      const result = statement.run(...normalized.values)
      return Number(result.changes ?? 0)
    },
    close() {
      database.close()
    },
  }
}

export type {
  CompanyRow,
  DepartmentRow,
  AgentRow,
  SkillRow,
  ConversationRow,
  MessageRow,
  PlaygroundDocumentRow,
  ReviewRecordRow,
  RoadmapPhaseRow,
  TemplateRow,
}
