#  Copyright 2023 Reid Swanson.
#
#  This file is part of scrachy.
#
#  scrachy is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  scrachy is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with scrachy.  If not, see <https://www.gnu.org/licenses/>.

# Standard Library
import copy
import logging

from collections import defaultdict

# 3rd Party Library
import pytest

from dotenv import load_dotenv
from integration.conftest import sync_engine_manager
from psycopg import Connection
from rwskit.sqlalchemy.engine import SyncAlchemyEngine
from rwskit.sqlalchemy.repository import ConflictResolutionStrategy
from scrapy.settings import Settings

# 1st Party Library
from scrachy.db.base import ScrachyBase
from scrachy.db.models import Response as CachedResponse
from scrachy.db.models import ScrapeHistory
from scrachy.db.repositories import SyncResponseRepository, SyncScrapeHistoryRepository

load_dotenv()


log = logging.getLogger("test_repositories")

log.debug("From test_repositories")


@pytest.fixture
def settings(
    settings_choices: dict[str, Settings], request: pytest.FixtureRequest
) -> Settings:
    return settings_choices[request.param]


# Note: It's difficult (maybe impossible?) to test if 'insert'/'upsert' is
# working without also testing 'find' and vice versa.
@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
@pytest.mark.parametrize("settings", ["defaults", "settings_2"], indirect=True)
def test_upsert_and_find(
    dialect: str,
    settings: Settings,
    cached_responses: list[CachedResponse],
    postgresql: Connection,
):
    # Create a copy because the objects could be modified by the upsert
    # process.
    cached_responses_copy = copy.deepcopy(cached_responses)

    with sync_engine_manager(dialect, postgresql) as sa_engine:
        engine = SyncAlchemyEngine(sa_engine, ScrachyBase)

        with engine.session_scope():
            response_repo = SyncResponseRepository(engine)
            history_repo = SyncScrapeHistoryRepository(engine)

            for exp_response in cached_responses_copy:
                history = ScrapeHistory(
                    fingerprint=exp_response.fingerprint,
                    scrape_timestamp=exp_response.scrape_timestamp,
                    body=exp_response.body,
                )
                response_repo.upsert(
                    exp_response, on_conflict=ConflictResolutionStrategy.UPDATE
                )
                history_repo.insert(history)

                # Don't assert anything here. It's complicated with the scrape_history
                # assert act_response == exp_response

            with engine.session_scope():
                response_repo = SyncResponseRepository(engine)

                sorted_responses = sorted(
                    cached_responses,
                    key=lambda e: (e.fingerprint, e.scrape_timestamp),
                    reverse=True,
                )
                expected_responses = []
                fingers = defaultdict(list)

                for r in sorted_responses:
                    if r.fingerprint not in fingers:
                        r.scrape_timestamp = r.scrape_timestamp
                        expected_responses.append(r)

                    fingers[r.fingerprint].append(r.body)

                # One at a time
                # Compare strings to avoid comparing the scrape history

                assert all([
                    str(e) == str(response_repo.find_by_fingerprint(e.fingerprint))
                    for e in expected_responses
                ])

                # All of them
                with engine.session_scope() as session:
                    act_responses = response_repo.find_all_models(session=session)
                    assert len(expected_responses) == len(act_responses)
                    assert all([
                        str(e) == str(a)
                        for e, a in zip(expected_responses, act_responses)
                    ])

                    # Make sure the scrape history has the correct number of entries
                    for act_response in act_responses:
                        act_history = sorted(
                            act_response.scrape_history,
                            key=lambda h: h.scrape_timestamp,
                            reverse=True,
                        )
                        exp_history = fingers[act_response.fingerprint]

                        assert len(exp_history) == len(act_history)
                        assert all([
                            exp == act.body
                            for exp, act in zip(exp_history, act_history)
                        ])
