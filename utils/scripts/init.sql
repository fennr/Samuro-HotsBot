BEGIN;

create domain battletag as varchar(20);

create domain discord_id as bigint;

create domain guild_id as bigint;

create type league_type as enum ('Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Master', 'Grandmaster');

create type winner_type as enum ('blue', 'red');

create sequence "Achievements_achiev_id_seq"
    as integer;

create sequence "EventHistory_event_id_seq"
    as integer;

create sequence "Teams_team_id_seq"
    as integer;

create table "Players"
(
    btag     battletag,
    id       discord_id not null
        constraint id_key
            primary key,
    guild_id guild_id,
    mmr      integer,
    league   league_type,
    division integer,
    team     integer
        constraint team_key
            references "Teams"
            on update set null on delete set null
);

comment on table "Players" is 'Таблица связей дискорд-батлнет и личных данных единых на все сервера';

create table "UserStats"
(
    id       discord_id not null
        constraint id_key
            references "Players"
            on update cascade on delete cascade,
    guild_id guild_id   not null,
    win      integer,
    lose     integer,
    points   integer,
    btag     battletag,
    constraint id
        primary key (id, guild_id)
);

comment on table "UserStats" is 'Данные о победах и поражениях по каждому серверу';

create table "EventHistory"
(
    time      timestamp,
    guild_id  guild_id,
    winner    winner_type,
    active    boolean,
    blue1     battletag,
    blue2     battletag,
    blue3     battletag,
    blue4     battletag,
    blue5     battletag,
    red1      battletag,
    red2      battletag,
    red3      battletag,
    red4      battletag,
    red5      battletag,
    event_id  serial not null,
    room_id   bigint,
    delta_mmr integer,
    points    integer,
    admin     varchar
);

comment on table "EventHistory" is 'Таблица проведенных ивентов';

create table "Achievements"
(
    id       serial   not null,
    guild_id guild_id not null,
    name     varchar,
    constraint "Achievements_pkey"
        primary key (id, guild_id)
);

comment on table "Achievements" is 'Таблица существующих достижений';

create table "UserAchievements"
(
    id          discord_id,
    guild_id    guild_id,
    achievement integer,
    date        date,
    constraint stats_key
        foreign key (id, guild_id) references "UserStats"
            on update cascade on delete cascade,
    constraint achive_key
        foreign key (guild_id, achievement) references "Achievements" (guild_id, id)
            on update cascade on delete cascade
);

comment on table "UserAchievements" is 'Связи между игроком и достижениями';

create table "Teams"
(
    id      serial not null
        constraint "Teams_pkey"
            primary key,
    name    varchar,
    leader  discord_id,
    members integer default 1,
    points  integer default 0
);

comment on table "Teams" is 'Таблица с данными команд';

create unique index teams_name_uindex
    on "Teams" (name);

create unique index teams_leader_uindex
    on "Teams" (leader);

END;