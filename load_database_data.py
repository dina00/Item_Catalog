from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from database_setup import Base, Categories, Items, Users

engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


cat1 = Categories(name="Eyes",
                  description="Makeup for the eyes.")
session.add(cat1)
session.commit()

item1 = Items(name="Mascara", description='''Mascara is used to enhance the
              eyelashes.''', categories=cat1)
session.add(item1)
session.commit()

item2 = Items(name="Eyeliner", description='''Eyeliner is used to define
              the eyes.''', categories=cat1)
session.add(item2)
session.commit()

item3 = Items(name="Eye Shadow", description='''Eye Shadow is applied on
              the eyelids and under the eyes.''', categories=cat1)
session.add(item3)
session.commit()


cat2 = Categories(name="Face", description="Makeup for the face.")
session.add(cat2)
session.commit()

item4 = Items(name="Foundation", description='''Foundation is
              applied to the face to create an even,
              uniform color to the complexion.''', categories=cat2)
session.add(item4)
session.commit()

item5 = Items(name="concealer", description='''A concealer is
              used to mask dark circles, age spots,
              large pores, and other small blemishes
              visible on the skin.''', categories=cat2)
session.add(item5)
session.commit()

item6 = Items(name="Blush", description='''Gives a flushed
              healthy complexion.''', categories=cat2)
session.add(item6)
session.commit()


cat3 = Categories(name="Lips", description="Makeup for the lips.")
session.add(cat3)
session.commit()

item7 = Items(name="Lipstick", description='''Apply colour and
              protection to the lips.''', categories=cat3)
session.add(item7)
session.commit()

item8 = Items(name="Lip Gloss", description='''Gives a glossy lustre
              and a subtle colour.''', categories=cat3)
session.add(item8)
session.commit()

cat4 = Categories(name="Nails", description="Nail beauty.")
session.add(cat4)
session.commit()

item9 = Items(name="Nail Polish", description='''Decorate your
              nails with nail polish.''', categories=cat4)
session.add(item9)
session.commit()

print("database loaded successfully...")
