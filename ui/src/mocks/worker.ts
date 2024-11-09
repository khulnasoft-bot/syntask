import { WorkPoolWorker } from '@/models'
import { MockFunction } from '@/services'

export const randomWorker: MockFunction<WorkPoolWorker, [Partial<WorkPoolWorker>?]> = function(overrides = {}) {
  return new WorkPoolWorker({
    id: this.create('id'),
    created: this.create('date'),
    updated: this.create('date'),
    workPoolId: this.create('id'),
    name: this.create('noun'),
    lastHeartbeatTime: this.create('date'),
    status: this.create('workerStatus'),
    clientVersion: this.create('string'),
    metadata: { 'integrations': [this.create('string'), this.create('string')] },
    heartbeatIntervalSeconds: this.create('number'),
    ...overrides,
  })
}