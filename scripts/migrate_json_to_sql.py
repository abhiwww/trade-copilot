import asyncio
import json
import uuid
from datetime import datetime
from dateutil import parser
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from app.db.models.trade_models import (
    Organization, User, TradeCase, Document, Conversation, Message, Notification
)
from app.db.base import Base

# Database URL (Synchronous for migration script)
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/trade_copilot"

def migrate():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("Starting migration from JSON to PostgreSQL...")

        # 1. Organizations
        with open("backend/data/orgs.json", "r") as f:
            orgs_data = json.load(f)

        org_mapping = {}
        for oid, data in orgs_data.items():
            # Standardize to UUID
            sql_id = uuid.UUID(oid) if len(oid) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, oid)
            org = Organization(id=sql_id, **data)
            session.merge(org)
            org_mapping[oid] = sql_id
        print(f"Migrated {len(orgs_data)} organizations.")

        # 2. Users
        with open("backend/data/users.json", "r") as f:
            users_data = json.load(f)

        user_mapping = {}
        for uid, data in users_data.items():
            sql_id = uuid.UUID(uid) if len(uid) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, uid)
            # Link to migrated org
            org_id = org_mapping.get(data.get('org_id'))
            if not org_id: continue # Skip users without valid org

            user = User(id=sql_id, org_id=org_id, **{k: v for k, v in data.items() if k != 'org_id'})
            session.merge(user)
            user_mapping[uid] = sql_id
        print(f"Migrated {len(users_data)} users.")

        # 3. Trade Cases
        with open("backend/data/cases.json", "r") as f:
            cases_data = json.load(f)

        case_mapping = {}
        for cid, data in cases_data.items():
            sql_id = uuid.UUID(cid) if len(cid) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, cid)
            org_id = org_mapping.get(data.get('org_id'))
            if not org_id: continue

            # Parse dates
            created_at = parser.parse(data.get('created_at')) if data.get('created_at') else datetime.utcnow()
            updated_at = parser.parse(data.get('updated_at')) if data.get('updated_at') else datetime.utcnow()

            case = TradeCase(
                id=sql_id,
                org_id=org_id,
                created_at=created_at,
                updated_at=updated_at,
                **{k: v for k, v in data.items() if k not in ['org_id', 'created_at', 'updated_at']}
            )
            session.merge(case)
            case_mapping[cid] = sql_id
        print(f"Migrated {len(cases_data)} trade cases.")

        # 4. Documents
        with open("backend/data/docs.json", "r") as f:
            docs_data = json.load(f)

        doc_mapping = {}
        for did, data in docs_data.items():
            sql_id = uuid.UUID(did) if len(did) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, did)
            case_id = case_mapping.get(data.get('case_id'))
            if not case_id: continue

            # Find org_id from the case
            case_json = cases_data.get(data.get('case_id'), {})
            org_id = org_mapping.get(case_json.get('org_id'))
            if not org_id: continue

            doc = Document(
                id=sql_id,
                case_id=case_id,
                org_id=org_id,
                **{k: v for k, v in data.items() if k not in ['case_id']}
            )
            session.merge(doc)
            doc_mapping[did] = sql_id
        print(f"Migrated {len(docs_data)} documents.")

        # 5. Conversations
        with open("backend/data/conversations.json", "r") as f:
            convos_data = json.load(f)

        convo_mapping = {}
        for cvid, data in convos_data.items():
            sql_id = uuid.UUID(cvid) if len(cvid) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, cvid)
            org_id = org_mapping.get(data.get('org_id'))
            user_id = user_mapping.get(data.get('user_id'))
            case_id = case_mapping.get(data.get('case_id'))

            if not org_id or not user_id: continue

            convo = Conversation(
                id=sql_id,
                org_id=org_id,
                user_id=user_id,
                case_id=case_id,
                **{k: v for k, v in data.items() if k not in ['org_id', 'user_id', 'case_id']}
            )
            session.merge(convo)
            convo_mapping[cvid] = sql_id
        print(f"Migrated {len(convos_data)} conversations.")

        # 6. Messages
        with open("backend/data/messages.json", "r") as f:
            msgs_data = json.load(f)

        for mid, data in msgs_data.items():
            sql_id = uuid.UUID(mid) if len(mid) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, mid)
            conv_id = convo_mapping.get(data.get('conversation_id'))
            if not conv_id: continue

            # Find org_id from conversation
            convo_json = convos_data.get(data.get('conversation_id'), {})
            org_id = org_mapping.get(convo_json.get('org_id'))
            if not org_id: continue

            msg = Message(
                id=sql_id,
                conversation_id=conv_id,
                org_id=org_id,
                **{k: v for k, v in data.items() if k not in ['conversation_id']}
            )
            session.merge(msg)
        print(f"Migrated {len(msgs_data)} messages.")

        # 7. Notifications
        with open("backend/data/notifications.json", "r") as f:
            notifs_data = json.load(f)

        for nid, data in notifs_data.items():
            sql_id = uuid.UUID(nid) if len(nid) == 36 else uuid.uuid5(uuid.NAMESPACE_DNS, nid)
            user_id = user_mapping.get(data.get('user_id'))
            if not user_id: continue

            # Find org_id from user
            user_json = users_data.get(data.get('user_id'), {})
            org_id = org_mapping.get(user_json.get('org_id'))
            if not org_id: continue

            notif = Notification(
                id=sql_id,
                user_id=user_id,
                org_id=org_id,
                **{k: v for k, v in data.items() if k not in ['user_id']}
            )
            session.merge(notif)
        print(f"Migrated {len(notifs_data)} notifications.")

        session.commit()
        print("Migration completed successfully!")

    except Exception as e:
        session.rollback()
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    migrate()
