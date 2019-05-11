-- MUST OPEN MYSQL WITH $ mysql --local-infile otherwise it will not work!

create database if not exists tabtracker;

use tabtracker;
-- user table, staff table, user table, menuItem table, payment table, ingredient table, recipe table
drop table if exists orderItem;
drop table if exists orders;
drop table if exists recipe;
drop table if exists menuItem;
drop table if exists ingredient;
drop table if exists payments;
drop table if exists staff;
drop table if exists session;
drop table if exists user;

create table menuItem (
    miid int auto_increment,
    name varchar(30),
    kind enum('drink','snack','candy','sandwich','soup', 'pastry', 'gluten-free'),
    price double,
    quantity int,
    primary key (miid)
);

load data local infile 'menuItems.csv'
INTO TABLE menuItem 
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

select * from menuItem;

show warnings;

create table ingredient (
    iid int auto_increment,
    name varchar(30),
    kind enum('bread', 'meat', 'cheese', 'free', '50-cent', '1-dollar', 'base'),
    price double,
    quantity int,
    primary key (iid)
);

load data local infile 'ingredients.csv'
INTO TABLE ingredient 
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

create table recipe (
-- intermediate table represented by the 'has' relationship between ingredient menuItem
    miid int,
    iid int,
    foreign key (miid) references menuItem (miid),
    foreign key (iid) references ingredient (iid),
    primary key (miid, iid)
);

load data local infile 'recipes.csv'
INTO TABLE recipe
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

create table user (
    username varchar(30),
    name varchar(30),
    balanceOwed double,
    primary key (username)
);

load data local infile 'directory_search.csv'
INTO TABLE user
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

create table staff (
    username varchar(30),
    hashed char(60) not null,
    foreign key (username) references user (username),
    primary key (username)
);

create table orders (
    oid int auto_increment,
    dt datetime,
    username varchar(30),
    foreign key (username) references user (username),
    primary key (oid)
);

create table orderItem (
    oid int,
    miid int,
    quantity int,
    foreign key (oid) references orders (oid),
    foreign key (miid) references menuItem (miid),
    primary key (oid, miid)
);

create table payments (
    pid int auto_increment primary key,
    username varchar(30),
    dt datetime,
    method enum('cash','venmo'),
    amount double,
    foreign key (username) references user (username)
);

-- create table session (
--     sid int auto_increment primary key,
--     st timestamp default current_timestamp,
--     username varchar(30),
--     foreign key (username) references user (username)
-- );

-- insert into user(name, username, balanceOwed)
-- values ("Mona Kashyap", "mkashyap", 0.00);
       
insert into staff(username) values ("hlotfy"),("elennonj"),("mkashyap"),("acamacho");
       
-- insert into orders(dt,username) values(now(),'hlotfy');
-- insert into orderItem(oid,miid,quantity) values((select oid from orders where username="hlotfy" limit 1),(select miid from menuItem where name="Yoohoo"),1);

-- insert into orders(dt,username) values(now(),"acamacho");
-- insert into orderItem(oid,miid,quantity) values((select oid from orders where username="acamacho" limit 1),(select miid from menuItem where name="Yogurt"),1);

-- insert into orders(dt,username) values(now(),"elennonj");
-- insert into orderItem(oid,miid,quantity) values((select oid from orders where username="elennonj" limit 1),(select miid from menuItem where name="San Pellegrino"),1);

-- insert into orders(dt,username) values(now(),"mkashyap");
-- insert into orderItem(oid,miid,quantity) values((select oid from orders where username="mkashyap" limit 1),(select miid from menuItem where name="Capri Sun"),1);

-- insert into orders(dt,username) values(now(),"lorthsmi");

-- insert into payments (username, dt, method, amount) values ("hlotfy", now(), "venmo", 1.50);
-- insert into payments (username, dt, method, amount) values ("mkashyap", now(), "cash", 0.50);

-- update user, payments set balanceOwed = balanceOwed - (select sum(payments.amount) from payments where payments.username = user.username) where user.username = payments.username;

-- select user.name, sum(menuItem.price) as 'Tab Balance Owed' from orders inner join user on orders.username=user.username inner join orderItem on orders.oid=orderItem.oid inner join menuItem on orderItem.miid=menuItem.miid group by orders.username; 

-- select name, balanceOwed from user where balanceOwed > 0;

-- select menuItem.name, menuItem.miid, menuItem.price, sum(ingredient.price) from menuItem inner join recipe on menuItem.miid=recipe.miid inner join ingredient on recipe.iid=ingredient.iid group by menuItem.miid order by menuItem.miid;

