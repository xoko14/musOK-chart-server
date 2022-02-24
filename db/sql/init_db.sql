create table users
(
    id       serial primary key,
    username text,
    pass     text
);

create type song_diff as
(
    difficulty text,
    chart text,
    charter text
);

create type albumart as
(
    image text,
    artist text
);

create table songs
(
    id          serial primary key,
    song_name    text,
    author      text,
    easy_diff   song_diff,
    normal_diff song_diff,
    hard_diff   song_diff,
    song_art    albumart,
    music   text,
    uploader    integer,
    constraint  fk_user foreign key(uploader) references users(id)
);