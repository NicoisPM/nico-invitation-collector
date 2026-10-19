/**
 * 创建邀请函管理表 (nico_invitations) 与预约报名信息表 (nico_invitation_signups)
 */
exports.up = async function (knex) {
  const hasNicoInvitations = await knex.schema.hasTable('nico_invitations');
  if (!hasNicoInvitations) {
    await knex.schema.createTable('nico_invitations', (table) => {
      table.increments('id').primary();
      table.string('title').notNullable().comment('邀请函标题');
      table.string('slug').unique().notNullable().comment('访问短路径标识');
      table.string('file_path').notNullable().comment('服务器静态文件相对路径');
      table.string('event_time').defaultTo('').comment('开课/活动时间');
      table.string('deadline').defaultTo('').comment('报名截止时间');
      table.string('organizer').defaultTo('').comment('主办/承办单位');
      table.string('status').defaultTo('active').comment('状态: active-进行中, closed-已结束');
      table.integer('view_count').defaultTo(0).comment('浏览次数');
      table.datetime('created_at').defaultTo(knex.fn.now());
      table.datetime('updated_at').defaultTo(knex.fn.now());
    });
  }

  const hasSignups = await knex.schema.hasTable('nico_invitation_signups');
  if (!hasSignups) {
    await knex.schema.createTable('nico_invitation_signups', (table) => {
      table.increments('id').primary();
      table.integer('nico_invitation_id').references('id').inTable('nico_invitations').onDelete('SET NULL');
      table.string('nico_invitation_title').defaultTo('').comment('所属邀请函标题');
      table.string('name').notNullable().comment('报名人姓名');
      table.string('phone').notNullable().comment('手机号');
      table.string('company').notNullable().comment('企业名称');
      table.string('title').defaultTo('').comment('职务');
      table.integer('count').defaultTo(1).comment('报名人数');
      table.text('note').defaultTo('').comment('备注/关注议题');
      table.string('status').defaultTo('pending').comment('状态: pending-待联系, contacted-已联系, confirmed-已确认, cancelled-已取消');
      table.text('admin_remark').defaultTo('').comment('后台教务跟进备注');
      table.string('ip').defaultTo('').comment('提交IP');
      table.datetime('created_at').defaultTo(knex.fn.now());
      table.datetime('updated_at').defaultTo(knex.fn.now());
    });
  }
};

exports.down = async function (knex) {
  await knex.schema.dropTableIfExists('nico_invitation_signups');
  await knex.schema.dropTableIfExists('nico_invitations');
};
