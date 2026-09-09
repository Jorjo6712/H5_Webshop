from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import Article
class ArticleService:
    def __init__(self, session: Session):
        self.session = session

    def get_article(self) -> List[Article]:
        articles = self.session.scalars(
            select(Article).order_by(Article.article_number)
        ).all()
        print(list(articles))
        return list(articles)