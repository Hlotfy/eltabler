-- MUST OPEN MYSQL WITH $ mysql --local-infile otherwise it will not work!

use tabtracker;
-- user table, staff table, user table, menuItem table, payment table, ingredient table, recipe table
drop table if exists orders;
drop table if exists recipe;
drop table if exists menuItem;
drop table if exists ingredient;
drop table if exists payments;
drop table if exists staff;
drop table if exists user;


create table menuItem (
    miid int auto_increment,
    name varchar(30),
    kind enum('drink','snack','candy','sandwich'),
    price float,
    quantity int,
    primary key (miid)
);

load data local infile 'snacks.csv'
INTO TABLE menuItem 
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

load data local infile 'sandwiches.csv'
INTO TABLE menuItem 
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

create table ingredient (
    iid int auto_increment,
    name varchar(30),
    kind enum('bread', 'meat', 'cheese', 'extra', 'base'),
    price float,
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
    name varchar(30),
    username varchar(30) NOT NULL UNIQUE,
    balanceOwed float,
    primary key (username)
);

load data local infile 'directory_search.csv'
INTO TABLE user
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

show warnings;

create table staff (
    username varchar(30),
    password varchar(30),
    foreign key (username) references user (username),
    primary key (username)
);

create table orders (
    oid int auto_increment,
    dt datetime,
    miid int,
    username varchar(30),
    foreign key (miid) references menuItem (miid),
    foreign key (username) references user (username),
    primary key (oid)
);

create table payments (
    pid int auto_increment,
    username varchar(30),
    dt datetime,
    method enum('cash','venmo'),
    amount float,
    foreign key (username) references user (username),
    primary key (pid)
);

select * from menuItem;
select * from ingredient;

insert into user(name, username, balanceOwed)
values ("Hala Lotfy", "hlotfy", 0), 
       ("Dee Dee Lennon-Jones", "elennonj", 0), 
       ("Mona Kashyap", "mkashyap", 0), 
       ("Aliza Camacho", "acamacho", 0);
       

insert into orders(dt,username,miid) values(now(),'hlotfy',(select miid from menuItem where name="San Pellegrino"));
insert into orders(dt,username,miid) values(now(),'hlotfy',(select miid from menuItem where name="Candy"));
insert into orders(dt,username,miid) values(now(),'hlotfy',(select miid from menuItem where name="Yogurt"));

insert into orders(dt,username,miid) values(now(),"acamacho",(select miid from menuItem where name="San Pellegrino"));
insert into orders(dt,username,miid) values(now(),"elennonj",(select miid from menuItem where name="Candy"));
insert into orders(dt,username,miid) values(now(),"mkashyap",(select miid from menuItem where name="Yogurt"));

select * from orders;

insert into orders(dt,username,miid) values(now(),'lorthsmi',(select miid from menuItem where name="Capri Sun"));

insert into orders(dt,username,miid) values(now(),'lorthsmi',(select miid from menuItem where name="Capri Sun"));

insert into payments (username, dt, method, amount) values ("hlotfy", now(), "venmo", 1.50);
insert into payments (username, dt, method, amount) values ("hlotfy", now(), "venmo", 0.50);

update user, orders, menuItem set user.balanceOwed = (select sum(menuItem.price) from orders inner join menuItem on orders.miid = menuItem.miid where orders.username=user.username) where user.username = orders.username;

select * from user where balanceOwed > 0;

update user, payments set balanceOwed = balanceOwed - (select sum(payments.amount) from payments where payments.username = user.username) where user.username = payments.username;

select * from recipe;

select menuItem.name, menuItem.price, sum(ingredient.price) as 'ingredients price' from recipe inner join menuItem on recipe.miid = menuItem.miid inner join ingredient on recipe.iid = ingredient.iid group by menuItem.miid order by menuItem.name;  

select recipe.miid, sum(ingredient.price) from recipe inner join ingredient on recipe.iid = ingredient.iid group by recipe.miid;

select user.name, sum(menuItem.price) as 'Tab Balance Owed' from orders inner join user on orders.username=user.username inner join menuItem on orders.miid=menuItem.miid group by orders.username; 

select name, balanceOwed from user where balanceOwed > 0;