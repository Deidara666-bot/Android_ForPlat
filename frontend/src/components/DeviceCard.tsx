import type { Device } from '../types/device'
import { connectionStateLabel, formatTime } from '../utils/labels'

export default function DeviceCard({ device }: { device: Device }) {
  const connected = device.connection_state === 'connected'
  return (
    <article className="card" style={{ marginTop: 12 }}>
      <h2>
        {device.manufacturer} {device.model}
      </h2>
      <dl className="kv">
        <dt>Serial</dt>
        <dd>{device.serial}</dd>
        <dt>Status</dt>
        <dd className={connected ? 'ok' : 'error'}>{connectionStateLabel(device.connection_state)}</dd>
        <dt>Android</dt>
        <dd>
          {device.android_version} (API {device.api_level})
        </dd>
        <dt>Build</dt>
        <dd>{device.device_build}</dd>
        <dt>Terakhir terlihat</dt>
        <dd>{formatTime(device.last_seen_at)}</dd>
      </dl>
    </article>
  )
}
