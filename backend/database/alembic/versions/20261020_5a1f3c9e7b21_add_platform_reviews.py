"""add platform reviews

Revision ID: 20261020_5a1f3c9e7b21
Revises: 20260420_111111111111
Create Date: 2026-10-20 00:00:00.000000
"""

from alembic import op


revision = "20261020_5a1f3c9e7b21"
down_revision = "20260420_111111111111"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IF NOT EXISTS: на чистой БД таблицу уже создаёт initial_schema (create_all по моделям)
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS platform_reviews (
            id BIGSERIAL PRIMARY KEY,
            author_name TEXT NOT NULL,
            author_position TEXT,
            company_name TEXT,
            author_role TEXT NOT NULL,
            city TEXT,
            rating INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT ck_platform_reviews_rating CHECK (rating BETWEEN 1 AND 5),
            CONSTRAINT ck_platform_reviews_author_role CHECK (author_role IN ('BUYER', 'SUPPLIER'))
        )
        """
    )

    # Стартовые отзывы — только в пустую таблицу, чтобы повторный прогон ничего не дублировал
    op.execute(
        """
        INSERT INTO platform_reviews
            (author_name, author_position, company_name, author_role, city, rating, comment, created_at)
        SELECT v.author_name, v.author_position, v.company_name, v.author_role, v.city, v.rating, v.comment, v.created_at
        FROM (VALUES
            ('Анна Соколова', 'Шеф-повар', 'ООО «Ресторан Вкусный Двор»', 'BUYER', 'Санкт-Петербург', 5,
             'Раньше обзванивали пять поставщиков, чтобы собрать одну закупку. Теперь сравниваю цены в каталоге и оформляю заказ за десять минут. Отдельно нравится, что статус заказа видно в кабинете — больше не нужно уточнять по телефону, едет ли машина.',
             TIMESTAMPTZ '2026-09-02 11:20:00+03'),
            ('Игорь Петров', 'Руководитель отдела продаж', 'Мясной Двор', 'SUPPLIER', 'Московская область', 5,
             'Заказы от ресторанов приходят в одно место — сразу с составом и суммой. Принимаем заявку, и остатки на складе списываются автоматически: путаницы с наличием стало заметно меньше.',
             TIMESTAMPTZ '2026-09-14 16:05:00+03'),
            ('Марина Ильина', 'Управляющая', 'Вкусный Уголок', 'BUYER', 'Казань', 4,
             'Удобный каталог и фильтры по региону и категории. Шаблон заказа экономит время на регулярных закупках. Хотелось бы ещё получать уведомления о новых поставщиках в нашем городе.',
             TIMESTAMPTZ '2026-09-27 09:40:00+03'),
            ('Олег Смирнов', 'Директор', 'Молочный Край', 'SUPPLIER', 'Санкт-Петербург', 5,
             'Через платформу к нам пришли рестораны, с которыми раньше не пересекались. Чат с покупателем прямо в кабинете — быстро согласовываем объёмы и сроки поставки.',
             TIMESTAMPTZ '2026-10-06 13:15:00+03'),
            ('Елена Кравцова', 'Менеджер по закупкам', 'Чистая Вода', 'BUYER', 'Краснодар', 4,
             'Документы и аналитика по заказам собраны в одном кабинете — удобно для отчётности. Интерфейс понятный, освоились за пару дней. Не хватает мобильного приложения, но сайт с телефона работает нормально.',
             TIMESTAMPTZ '2026-10-15 18:30:00+03')
        ) AS v(author_name, author_position, company_name, author_role, city, rating, comment, created_at)
        WHERE NOT EXISTS (SELECT 1 FROM platform_reviews)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS platform_reviews")
