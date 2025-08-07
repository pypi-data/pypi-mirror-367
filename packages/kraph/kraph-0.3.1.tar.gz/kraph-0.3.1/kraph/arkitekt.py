import json
from fakts_next.contrib.rath.auth import FaktsAuthLink
from fakts_next.models import Requirement
from kraph.contrib.fakts.datalayer import FaktsKraphDataLayer
from kraph.kraph import Kraph
from kraph.links.upload import UploadLink
from kraph.rath import KraphLinkComposition, KraphRath
from rath.links.split import SplitLink
from fakts_next.contrib.rath.aiohttp import FaktsAIOHttpLink
from fakts_next.contrib.rath.graphql_ws import FaktsGraphQLWSLink
from graphql import OperationType
from fakts_next import Fakts


from arkitekt_next.service_registry import (
    BaseArkitektService,
    Params,
    get_default_service_registry,
)
import os


class ArkitektNextKraph(Kraph):
    rath: KraphRath


def build_relative_path(*path: str) -> str:
    return os.path.join(os.path.dirname(__file__), *path)


class KraphService(BaseArkitektService):
    def get_service_name(self):
        return "kraph"

    def build_service(
        self,
        fakts: Fakts,
        params: Params,
    ):
        datalayer = FaktsKraphDataLayer(fakts_group="datalayer", fakts=fakts)

        return ArkitektNextKraph(
            rath=KraphRath(
                link=KraphLinkComposition(
                    auth=FaktsAuthLink(fakts=fakts),
                    upload=UploadLink(
                        datalayer=datalayer,
                    ),
                    split=SplitLink(
                        left=FaktsAIOHttpLink(
                            fakts_group="kraph", fakts=fakts, endpoint_url="FAKE_URL"
                        ),
                        right=FaktsGraphQLWSLink(
                            fakts_group="kraph", fakts=fakts, ws_endpoint_url="FAKE_URL"
                        ),
                        split=lambda o: o.node.operation != OperationType.SUBSCRIPTION,
                    ),
                )
            ),
            datalayer=datalayer,
        )

    def get_requirements(self):
        return [
            Requirement(
                key="kraph",
                service="live.arkitekt.kraph",
                description="An instance of ArkitektNext kraph to relate entities",
            ),
            Requirement(
                key="datalayer",
                service="live.arkitekt.s3",
                description="An instance of ArkitektNext Datalayer to make requests to the user's data",
                optional=True,
            ),
        ]

    def get_graphql_schema(self):
        schema_graphql_path = build_relative_path("api", "schema.graphql")
        with open(schema_graphql_path) as f:
            return f.read()

    def get_turms_project(self):
        turms_prject = build_relative_path("api", "project.json")
        with open(turms_prject) as f:
            return json.loads(f.read())


get_default_service_registry().register(KraphService())
