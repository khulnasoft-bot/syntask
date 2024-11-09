import { CollectionItem, CollectionsResponse, SyntaskWorkerCollectionResponse, WorkerCollectionItem } from '@/models'
import { Api } from '@/services/Api'
import { mapper } from '@/services/Mapper'

export class CollectionsApi extends Api {
  protected override routePrefix = '/collections'

  public getFlowCollection(): Promise<CollectionItem[]> {
    return this.get<CollectionsResponse>('/views/aggregate-flow-metadata')
      .then(({ data }) => mapper.map('CollectionResponse', data, 'CollectionItems'))
  }

  public getWorkerCollection(): Promise<WorkerCollectionItem[]> {
    return this.get<SyntaskWorkerCollectionResponse>('/views/aggregate-worker-metadata')
      .then(({ data }) => mapper.map('SyntaskWorkerCollectionResponse', data, 'WorkerCollectionItem'))
  }
}