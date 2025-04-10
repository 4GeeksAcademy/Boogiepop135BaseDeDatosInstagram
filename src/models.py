from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import ForeignKey, Text, DateTime, Integer, String, Boolean, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    _password: Mapped[str] = mapped_column('password', String(256), nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(100))
    biografia: Mapped[str] = mapped_column(Text, default="")
    foto_perfil: Mapped[str] = mapped_column(String(255), default="default.jpg")
    privado: Mapped[bool] = mapped_column(Boolean, default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relaciones
    posts: Mapped[list['Post']] = relationship(back_populates='usuario', cascade='all, delete-orphan')
    comentarios: Mapped[list['Comentario']] = relationship(back_populates='usuario')
    seguidores = relationship('Seguidor', foreign_keys='Seguidor.usuario_id', back_populates='usuario')
    seguidos = relationship('Seguidor', foreign_keys='Seguidor.seguidor_id', back_populates='seguidor')
    
    @property
    def password(self):
        raise AttributeError('La contraseña no es legible')
    
    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)
    
    def verificar_password(self, password):
        return check_password_hash(self._password, password)
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "nombre_completo": self.nombre_completo,
            "foto_perfil": self.foto_perfil,
            "biografia": self.biografia,
            "privado": self.privado
        }

class Post(db.Model):
    __tablename__ = 'posts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'), nullable=False)
    imagen_url: Mapped[str] = mapped_column(String(255), nullable=False)
    pie_de_foto: Mapped[str] = mapped_column(Text)
    ubicacion: Mapped[str] = mapped_column(String(100))
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relaciones
    usuario: Mapped['Usuario'] = relationship(back_populates='posts')
    comentarios: Mapped[list['Comentario']] = relationship(back_populates='post', cascade='all, delete-orphan')
    likes: Mapped[list['Like']] = relationship(back_populates='post', cascade='all, delete-orphan')
    
    def serialize(self):
        return {
            "id": self.id,
            "imagen_url": self.imagen_url,
            "pie_de_foto": self.pie_de_foto,
            "ubicacion": self.ubicacion,
            "creado_en": self.creado_en.isoformat(),
            "usuario": self.usuario.serialize(),
            "total_likes": len(self.likes),
            "total_comentarios": len(self.comentarios)
        }

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relaciones
    usuario: Mapped['Usuario'] = relationship(back_populates='comentarios')
    post: Mapped['Post'] = relationship(back_populates='comentarios')
    
    def serialize(self):
        return {
            "id": self.id,
            "contenido": self.contenido,
            "creado_en": self.creado_en.isoformat(),
            "usuario": self.usuario.serialize()
        }

class Like(db.Model):
    __tablename__ = 'likes'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relaciones
    usuario: Mapped['Usuario'] = relationship('Usuario')
    post: Mapped['Post'] = relationship(back_populates='likes')
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'post_id', name='unique_like'),
    )

class Seguidor(db.Model):
    __tablename__ = 'seguidores'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'), nullable=False)  # Usuario que es seguido
    seguidor_id: Mapped[int] = mapped_column(ForeignKey('usuarios.id'), nullable=False)  # Usuario que sigue
    creado_en: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    aceptado: Mapped[bool] = mapped_column(Boolean, default=False)  # Para cuentas privadas
    
    # Relaciones
    usuario = relationship('Usuario', foreign_keys=[usuario_id], back_populates='seguidores')
    seguidor = relationship('Usuario', foreign_keys=[seguidor_id], back_populates='seguidos')
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'seguidor_id', name='unique_follow'),
    )