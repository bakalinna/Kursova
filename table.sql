drop table if exists realties;
create table realties (
  id serial primary key not null,
  type text not null,
  mark integer not null,
  price varchar(80) not null,
  name text not null,
  surname text not null,
  number varchar(80) not null,
  reservation_date date not null
);