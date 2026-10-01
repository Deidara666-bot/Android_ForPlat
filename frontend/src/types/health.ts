export interface Health {
  status: string
  app_env: string
  database: string
  alembic_revision: string | null
  app_version: string
}

export type HealthResult =
  | { kind: 'ok'; health: Health }
  | { kind: 'database_unreachable' }
  | { kind: 'backend_unreachable' }
