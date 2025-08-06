from airflow_providers_onehouse.operators.base_onehouse import BaseOnehouseOperator


class OnehouseCreateClusterOperator(BaseOnehouseOperator):
    """
    Operator to create a cluster in Onehouse.

    :param cluster_name: Name of the cluster to create.
    :param cluster_type: Type of the cluster (e.g., 'SPARK').
    :param parameters: List of parameters for the cluster.
    :param conn_id: Airflow connection ID for Onehouse.
    :return: The cluster name of the created cluster.
    """

    def __init__(self, cluster_name: str, cluster_type: str, max_ocu: int, min_ocu: int, parameters: dict | None = None, conn_id: str = "onehouse_default", *args, **kwargs):
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.cluster_name = cluster_name
        self.cluster_type = cluster_type
        self.max_ocu = max_ocu
        self.min_ocu = min_ocu
        self.parameters = parameters or {}

    def execute(self, context):
        sql = self._build_create_cluster_sql()
        self.log.info("Creating Onehouse cluster '%s' with SQL: %s", self.cluster_name, sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Created Onehouse cluster '%s', request_id='%s'", self.cluster_name, request_id)
        self.hook.wait_for_status(request_id, timeout=1200)
        return self.cluster_name

    def _build_create_cluster_sql(self) -> str:
        sql = (
            f"CREATE CLUSTER {self.cluster_name} "
            f"TYPE = '{self.cluster_type}' "
            f"MAX_OCU = {self.max_ocu} "
            f"MIN_OCU = {self.min_ocu}"
        )
        # Add additional parameters if provided
        if self.parameters:
            with_clause = ', '.join(f"'{k}' = '{v}'" for k, v in self.parameters.items())
            sql += f"\n  WITH {with_clause}"
        return sql


class OnehouseDeleteClusterOperator(BaseOnehouseOperator):
    """
    Operator to delete a cluster in Onehouse.

    :param cluster_name: Name of the cluster to delete.
    :param conn_id: Airflow connection ID for Onehouse.
    :return: The cluster name of the deleted cluster.
    """

    template_fields = ("cluster_name",)

    def __init__(self, cluster_name: str, conn_id: str = "onehouse_default", *args, **kwargs):
        super().__init__(conn_id=conn_id, *args, **kwargs)
        self.cluster_name = cluster_name

    def execute(self, context):
        sql = self._build_delete_cluster_sql()
        self.log.info("Deleting Onehouse cluster '%s' with SQL: %s", self.cluster_name, sql)
        request_id = self.hook.submit_sql(sql)
        self.log.info("Deleted Onehouse cluster '%s', request_id='%s'", self.cluster_name, request_id)
        self.hook.wait_for_status(request_id, timeout=1200)
        return self.cluster_name

    def _build_delete_cluster_sql(self) -> str:
        return f"DELETE CLUSTER {self.cluster_name}"
