from __future__ import annotations

from linkmerce.parse import QueryParser
import functools

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal
    from linkmerce.common import JsonObject


class _CatalogParser(QueryParser):
    object_type: Literal["catalogs","products"]

    def check_errors(func):
        @functools.wraps(func)
        def wrapper(self: _CatalogParser, response: JsonObject, *args, **kwargs):
            if isinstance(response, dict):
                if not response.get("errors"):
                    return func(self, response, *args, **kwargs)
                else:
                    self.raise_request_error(response)
            else:
                self.raise_parse_error("Could not parse the HTTP response.")
        return wrapper

    def raise_request_error(self, response: dict):
        from linkmerce.utils.map import hier_get
        from linkmerce.common import RequestError
        msg = hier_get(response, ["errors",0,"message"]) or "null"
        raise RequestError(f"An error occurred during the request: {msg}")

    @check_errors
    def parse(self, response: JsonObject, **kwargs) -> list[dict]:
        data = response["data"][self.object_type]["items"]
        return self.select(data, self.make_query(**kwargs)) if data else list()


class BrandCatalog(_CatalogParser):
    object_type = "catalogs"

    def make_query(self, **kwargs) -> str:
        query = """
        SELECT
            TRY_CAST(id AS INT64) AS nvMid,
            name AS catalogName,
            TRY_CAST(NULLIF(makerSeq, '0') AS INT64) AS makerId,
            makerName,
            TRY_CAST(brandSeq AS INT64) AS brandId,
            brandName,
            TRY_CAST(categoryId AS INT32) AS categoryId,
            categoryName,
            TRY_CAST(SPLIT_PART(fullCategoryId, '>', 1) AS INT32) AS categoryId1,
            NULLIF(SPLIT_PART(fullCategoryName, '>', 1), '') AS categoryName1,
            TRY_CAST(SPLIT_PART(fullCategoryId, '>', 2) AS INT32) AS categoryId2,
            NULLIF(SPLIT_PART(fullCategoryName, '>', 2), '') AS categoryName2,
            TRY_CAST(SPLIT_PART(fullCategoryId, '>', 3) AS INT32) AS categoryId3,
            NULLIF(SPLIT_PART(fullCategoryName, '>', 3), '') AS categoryName3,
            TRY_CAST(SPLIT_PART(fullCategoryId, '>', 4) AS INT32) AS categoryId4,
            NULLIF(SPLIT_PART(fullCategoryName, '>', 4), '') AS categoryName4,
            image.SRC AS imageUrl,
            TRY_CAST(lowestPrice AS INT64) AS salesPrice,
            productCount,
            totalReviewCount AS reviewCount,
            TRY_CAST(reviewRating AS INT8) AS reviewRating,
            DATE_TRUNC('SECOND', TRY_CAST(registerDate AS TIMESTAMP)) AS registerDate
        FROM {{ table }}
        """
        return self.render_query(query)


class BrandProduct(_CatalogParser):
    object_type = "products"

    def make_query(self, mall_seq: int | str | None = None, **kwargs) -> str:
        query = """
        SELECT
            TRY_CAST(id AS INT64) AS nvMid,
            {{ product_id }} AS mallPid,
            TRY_CAST(catalogId AS INT64) AS catalogId,
            name AS productName,
            TRY_CAST(NULLIF(makerSeq, '0') AS INT64) AS makerId,
            makerName,
            TRY_CAST(brandSeq AS INT64) AS brandId,
            brandName,
            TRY_CAST({{ mall_seq }} AS INT64) AS mallSeq,
            mallName,
            TRY_CAST(categoryId AS INT32) AS categoryId,
            categoryName,
            TRY_CAST(SPLIT_PART(fullCategoryId, '>', 1) AS INT32) AS categoryId1,
            NULLIF(SPLIT_PART(fullCategoryName, '>', 1), '') AS categoryName1,
            TRY_CAST(SPLIT_PART(fullCategoryId, '>', 2) AS INT32) AS categoryId2,
            NULLIF(SPLIT_PART(fullCategoryName, '>', 2), '') AS categoryName2,
            TRY_CAST(SPLIT_PART(fullCategoryId, '>', 3) AS INT32) AS categoryId3,
            NULLIF(SPLIT_PART(fullCategoryName, '>', 3), '') AS categoryName3,
            TRY_CAST(SPLIT_PART(fullCategoryId, '>', 4) AS INT32) AS categoryId4,
            NULLIF(SPLIT_PART(fullCategoryName, '>', 4), '') AS categoryName4,
            outLinkUrl AS mallPurl,
            image.SRC AS imageUrl,
            TRY_CAST(lowestPrice AS INT64) AS salesPrice,
            DATE_TRUNC('SECOND', TRY_CAST(registerDate AS TIMESTAMP)) AS registerDate
        FROM {{ table }};
        """
        product_id = "mallProductId" if mall_seq is None else "TRY_CAST(mallProductId AS INT64)"
        return self.render_query(query, mall_seq=mall_seq, product_id=product_id)


class ProductPrice(BrandProduct):
    object_type = "products"

    def make_query(self, mall_seq: int | str | None = None, **kwargs) -> str:
        query = """
        SELECT * EXCLUDE (seq)
        FROM (
            SELECT
                {{ product_id }} AS mallPid,
                TRY_CAST({{ mall_seq }} AS INT64) AS mallSeq,
                TRY_CAST(categoryId AS INT32) AS categoryId,
                TRY_CAST(lowestPrice AS INT64) AS salesPrice,
                {{ yesterday }} AS updateDate,
                ROW_NUMBER() OVER (PARTITION BY mallPid) AS seq
            FROM {{ table }}
        ) WHERE (mallPid IS NOT NULL) AND (seq = 1);
        """
        product_id = "mallProductId" if mall_seq is None else "TRY_CAST(mallProductId AS INT64)"
        yesterday = self.curret_date(interval=-1)
        return self.render_query(query, mall_seq=mall_seq, product_id=product_id, yesterday=yesterday)


class ProductList(BrandProduct):
    object_type = "products"

    def make_query(self, mall_seq: int | str | None = None, **kwargs) -> str:
        query = """
        SELECT * EXCLUDE (seq)
        FROM (
            SELECT
                {{ product_id }} AS mallPid,
                TRY_CAST({{ mall_seq }} AS INT64) AS mallSeq,
                TRY_CAST(categoryId AS INT32) AS categoryId,
                TRY_CAST(SPLIT_PART(fullCategoryId, '>', 3) AS INT32) AS categoryId3,
                name AS productName,
                TRY_CAST(lowestPrice AS INT64) AS salesPrice,
                TRY_CAST(registerDate AS DATE) AS registerDate,
                {{ today }} AS updateDate,
                ROW_NUMBER() OVER (PARTITION BY mallPid) AS seq
            FROM {{ table }}
        ) WHERE (mallPid IS NOT NULL) AND (seq = 1);
        """
        product_id = "mallProductId" if mall_seq is None else "TRY_CAST(mallProductId AS INT64)"
        today = self.curret_date()
        return self.render_query(query, mall_seq=mall_seq, product_id=product_id, today=today)
