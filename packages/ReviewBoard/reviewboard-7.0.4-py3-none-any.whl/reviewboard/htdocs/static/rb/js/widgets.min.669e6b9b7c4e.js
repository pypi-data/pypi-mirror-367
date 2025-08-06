!function(){"use strict";RB.RelatedUserSelectorView=Djblets.RelatedObjectSelectorView.extend({searchPlaceholderText:gettext("Search for users..."),optionTagName:"tr",optionTemplate:_.template(`<div>
 <% if (useAvatars && avatarHTML) { %><%= avatarHTML %><% } %>
 <% if (fullname) { %>
  <span class="title"><%- fullname %></span>
  <span class="description">(<%- username %>)</span>
 <% } else { %>
  <span class="title"><%- username %></span>
 <% } %>
</div>`),selectedOptionTemplate:_.template(`<% if (useAvatars) { %>
 <td><%= avatarHTML %></td>
<% } %>
<% if (fullname) { %>
 <td><%- fullname %></td>
 <td>(<%- username %>)</td>
<% } else { %>
 <td><%- username %></td>
 <td></td>
<% } %>
<td>
 <a href="#" role="button"
    class="remove-item ink-i-delete-item"
    aria-label="<%- removeText %>"
    title="<%- removeText %>"
    ></a>
</td>`),template:_.template(`<select placeholder=""
        class="related-object-options"></select>
<% if (multivalued) { %>
<table class="related-object-selected"></table>
<% } %>`),autoAddClose:!1,initialize(e){Djblets.RelatedObjectSelectorView.prototype.initialize.call(this,_.defaults({selectizeOptions:{searchField:["fullname","username"],sortField:[{field:"fullname"},{field:"username"}],valueField:"username"}},e)),this._localSitePrefix=e.localSitePrefix||"",this._useAvatars=!!e.useAvatars},renderOption(e){return $(this.optionTemplate(_.extend({useAvatars:this._useAvatars},e)))},renderSelectedOption(e){const t=$(this.selectedOptionTemplate(_.extend({removeText:gettext("Remove user"),useAvatars:this._useAvatars},e)));return t.find(".remove-item").on("click",()=>this._onItemRemoved(t,e)),t},loadOptions(e,t){var a={fullname:1,"only-fields":"avatar_html,fullname,id,username","only-links":"","render-avatars-at":"20"};0!==e.length&&(a.q=e),$.ajax({type:"GET",url:""+SITE_ROOT+this._localSitePrefix+"api/users/",data:a,success(e){t(e.users.map(e=>({avatarHTML:e.avatar_html[20],fullname:e.fullname,id:e.id,username:e.username})))},error(...e){console.error("User query failed",e),t()}})}});{const t=_.template(`<div>
 <span class="title"><%- name %></span>
</div>`);RB.RelatedRepoSelectorView=Djblets.RelatedObjectSelectorView.extend({searchPlaceholderText:gettext("Search for repositories..."),initialize(e){Djblets.RelatedObjectSelectorView.prototype.initialize.call(this,_.defaults({selectizeOptions:{searchField:["name"],sortField:[{field:"name"}],valueField:"name"}},e)),this._localSitePrefix=e.localSitePrefix||""},renderOption(e){return t(e)},loadOptions(e,t){var a={"only-fields":"name,id"};0!==e.length&&(a.q=e),$.ajax({type:"GET",url:""+SITE_ROOT+this._localSitePrefix+"api/repositories/",data:a,success:e=>{t(e.repositories.map(e=>({name:e.name,id:e.id})))},error:(...e)=>{console.error("Repository query failed",e),t()}})}})}{const a=_.template(`<div>
 <span class="title"><%- name %> : <%- display_name %></span>
</div>`);RB.RelatedGroupSelectorView=Djblets.RelatedObjectSelectorView.extend({searchPlaceholderText:gettext("Search for groups..."),initialize(e){Djblets.RelatedObjectSelectorView.prototype.initialize.call(this,_.defaults({selectizeOptions:{searchField:["name","display_name"],sortField:[{field:"name"},{field:"display_name"}],valueField:"name"}},e)),this._localSitePrefix=e.localSitePrefix||"",this._inviteOnly=e.inviteOnly,this._showInvisible=e.showInvisible},renderOption(e){return a(e)},loadOptions(e,t){var a={"only-fields":"invite_only,name,display_name,id",displayname:1};0!==e.length&&(a.q=e),this._inviteOnly&&(a["invite-only"]="1"),this._showInvisible&&(a["show-invisible"]="1"),$.ajax({type:"GET",url:""+SITE_ROOT+this._localSitePrefix+"api/groups/",data:a,success:e=>{t(e.groups.map(e=>({name:e.name,display_name:e.display_name,id:e.id,invite_only:e.invite_only})))},error:(...e)=>{console.error("Group query failed",e),t()}})}})}}.call(this);
