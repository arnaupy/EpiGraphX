from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from utils.base import Base


# class Reflected(DeferredReflection):
#     __abstract__ = True

def create_vector_table(dtype, class_name="Vector"):
    
    class Vector(Base):
        __tablename__ = class_name.lower()
        __table_args__ = {'extend_existing': True}
        id: Mapped[str] = mapped_column(primary_key=True)
        item_position: Mapped[int]
        item_value: Mapped[dtype]
        
        
        def __init__(self, *args, **kwargs):
            self.item_position = args[0]
            self.item_value = args[1]
            self.__class__.__name__ = class_name
            
            for attribute_name, attribute_value in kwargs.items():
                setattr(self, attribute_name, attribute_value)
            
        
        def __repr__(self):
            return f"{self.__class__.__name__}({self.item_position}, {self.item_value})"

    return Vector

    
        
    
    # ref_table_id: Mapped[str] = mapped_column(ForeignKey(f"{__tablename__}.id"))
    # id = Column("id", Integer, nullable = False, primary_key = True, autoincrement= True)
    # network_id = Column("network_id", String, ForeignKey("networks.id"), nullable = False)
    # item_position = Column("item_position", Integer, nullable = False)
    # item_value = Column("item_value", Integer, nullable = False)
    
    # def __init__(self, network_id, item_position, item_value):
    #     self.network_id = network_id
    #     self.item_position = item_position
    #     self.item_value = item_value
        
        
    # def __repr__(self):
    #     return f"({self.network_id}) {self.__tablename__} : pos({self.item_position}) : value({self.item_value})" 