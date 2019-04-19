use tabtracker;


select * from orders;

insert into orders(dt,username) values(now(),"lorthsmi");

-- insert into orders(dt,username) values(now(),"lorthsmi");

insert into payments (username, dt, method, amount) values ("hlotfy", now(), "venmo", 1.50);
insert into payments (username, dt, method, amount) values ("mkashyap", now(), "cash", 0.50);

-- update user, orders, menuItem set user.balanceOwed = (select sum(menuItem.price) from orders inner join menuItem on orders.miid = menuItem.miid where orders.username=user.username) where user.username = orders.username;

-- select * from user where balanceOwed > 0;

update user, payments set balanceOwed = balanceOwed - (select sum(payments.amount) from payments where payments.username = user.username) where user.username = payments.username;

select * from recipe;

select menuItem.name, menuItem.price, sum(ingredient.price) as 'ingredients price' from recipe inner join menuItem on recipe.miid = menuItem.miid inner join ingredient on recipe.iid = ingredient.iid group by menuItem.miid order by menuItem.name;  

select recipe.miid, sum(ingredient.price) from recipe inner join ingredient on recipe.iid = ingredient.iid group by recipe.miid;

select user.name, sum(menuItem.price) as 'Tab Balance Owed' from orders inner join user on orders.username=user.username inner join orderItem on orders.oid=orderItem.oid inner join menuItem on orderItem.miid=menuItem.miid group by orders.username; 

select name, balanceOwed from user where balanceOwed > 0;

select menuItem.name, menuItem.miid, menuItem.price, sum(ingredient.price) from menuItem inner join recipe on menuItem.miid=recipe.miid inner join ingredient on recipe.iid=ingredient.iid group by menuItem.miid order by menuItem.miid;

insert into orders(dt,username) values(now(),'hlotfy');
insert into orderItem (oid,miid,quantity) values ((select max(oid) from orders where username="hlotfy"),(select miid from menuItem where name="ABCD"), 1);
insert into orderItem (oid,miid,quantity) values ((select max(oid) from orders where username="hlotfy"),(select miid from menuItem where name="San Pellegrino"), 2);

-- returns all items in every order, as well as their unit price, their total item price, and their quantity
select orders.*, menuItem.name, menuItem.price, orderItem.quantity, (menuItem.price * orderItem.quantity) as "item total" from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username="hlotfy" and orders.oid=1;

-- returns total for each order --
select orders.oid, orders.dt, orders.username, sum(menuItem.price * orderItem.quantity) as "order total" from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username="hlotfy" group by orderItem.oid;

select orders.oid, orders.dt, orders.username, sum(menuItem.price * orderItem.quantity) as "order total" from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) group by orderItem.oid;

select orders.*, menuItem.name, menuItem.price, orderItem.quantity, (menuItem.price * orderItem.quantity) as "item total" from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username="hlotfy" and orders.oid=1;

select orderItem.*, menuItem.name from orderItem inner join menuItem on (orderItem.miid=menuItem.miid) where oid=1;    

insert into orderItem (oid,miid,quantity) values ((select max(oid) from orders where username="hlotfy"),(select miid from menuItem where name="Bread Serious"), 1), ((select max(oid) from orders where username="hlotfy"),(select miid from menuItem where name="Candy"), 3);

-- returns all empty orders (orders that do not have any orderItems)
select orders.oid from orders left join orderItem on (orders.oid=orderItem.oid) where orderItem.oid is NULL;

delete from orders where oid in (select orders.oid from orders left join orderItem on (orders.oid=orderItem.oid) where orderItem.oid is NULL); 

delete from orders where oid in (25,26,27,28,34,35,36,37,38,39,40,41,42,43,44,45,56);

-- calculate balance owed
select orders.username, sum(menuItem.price * orderItem.quantity) as 'total' from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) group by orders.username; 

select sum(menuItem.price * orderItem.quantity) as 'total' from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username=%s,(username,);

insert into orderItem (oid,miid,quantity) values ((select max(oid) from orders where username="elennonj"),(select miid from menuItem where name = "Bread Serious"), 10);

-- update individual balanceOwed
update user,orders set balanceOwed = 
    (select sum(menuItem.price * orderItem.quantity) as 'total' 
    from orders 
        inner join 
        orderItem 
            on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where orders.username="hlotfy") where user.username="hlotfy";

-- update everyone's balanceOwed
update user,orders set balanceOwed = (select sum(menuItem.price * orderItem.quantity) as 'total' from orders left join orderItem on (orders.oid=orderItem.oid) left join menuItem on (orderItem.miid=menuItem.miid) where orders.username=user.username);

update user,orders,payments set balanceOwed = ((select (sum(menuItem.price * orderItem.quantity)-sum(payments.amount)) as 'total' from orders left join orderItem on (orders.oid=orderItem.oid) left join menuItem on (orderItem.miid=menuItem.miid) left join payments on (user.username=payments.username) where orders.username=user.username, user.username<>payments.username);

-- add most recent order total to balance

update user,orders set balanceOwed = balanceOwed + (select sum(menuItem.price * orderItem.quantity) from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where user.username="hlotfy" group by orders.oid limit 1) where user.username="hlotfy"; 

-- delete most recent order total from balance
update user,orders set balanceOwed = balanceOwed - (select sum(menuItem.price * orderItem.quantity) from orders inner join orderItem on (orders.oid=orderItem.oid) inner join menuItem on (orderItem.miid=menuItem.miid) where user.username="hlotfy" group by orders.oid limit 1) where user.username="hlotfy"; 

-- subtract most recent payment amount from balance
update user,payments set balanceOwed = balanceOwed - (select amount from payments where username="hlotfy" limit 1) where user.username="hlotfy";        
