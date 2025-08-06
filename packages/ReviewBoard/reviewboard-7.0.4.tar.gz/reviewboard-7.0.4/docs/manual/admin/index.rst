.. _administration-guide:

====================
Administration Guide
====================


.. _installing-reviewboard-toc:

Installing Review Board
=======================

Ready to get started with Review Board? We've made it pretty easy, depending
on your platform.

Installation will happen in two steps:

* **Step 1: Install Review Board through:**

  * :doc:`The Review Board Installer <installation/installer>`
  * :doc:`Official Docker images <installation/docker>`

  If you have special requirements, you can instead follow step-by-step
  instructions to manually install Review Board for:

  * :doc:`Linux <installation/linux>`
  * :doc:`macOS <installation/osx>`
  * :doc:`Windows <installation/windows>`

* :doc:`Step 2: Create your site directory <installation/creating-sites>`

  Learn how to create your database and Review Board site directory, configure
  SELinux, and set up a web server.


.. _upgrading-reviewboard-toc:

Upgrading Review Board
======================

When you're ready to upgrade to a new version of Review Board, simply follow
these steps:

* :doc:`Step 1: Upgrade the Review Board packages
  <upgrading/upgrading-reviewboard>`
* :doc:`Step 2: Upgrade your site directory <upgrading/upgrading-sites>`


Optimizing/Scaling Your Server
==============================

Once you have things running, you'll want to make sure things are working
at peak performance by following our guides.

* :doc:`Introduction to optimizing and scaling Review Board <optimization/general>`
* :ref:`Recommended hardware <recommended-hardware>`
* :ref:`Optimizing memcached <optimizing-memcached>`
* :ref:`Setting diff limits <setting-diff-limits>`
* :ref:`Scaling your deployment <scaling-deployment>`
* :ref:`Troubleshooting performance problems <troubleshooting-performance>`


Monitoring Your Server
======================

To ensure things are running smoothly, and to handle auto-scaling of services,
you'll want to monitor your Review Board servers.

* :doc:`Health checks <monitoring/health-checks>`


The Administration UI
=====================

The Administration UI provides configuration options, database management,
news updates and system information. This area is available to all users with
:ref:`staff status <staff-status>` and can be reached by clicking
:guilabel:`Admin` in your account navigation menu in the top-right of any
page.

The Administration UI is composed of four main areas:

* :doc:`Admin Dashboard <admin-ui/dashboard>`
* :doc:`Settings <configuration/settings>`
* :doc:`Database <admin-ui/database>`
* :doc:`Extensions <extensions/index>`
* :doc:`Integrations <integrations/index>`


.. _configuration-topics:

Configuring Review Board
========================

After your site is set up, you may want to go through settings and set up your
authentication backend (if using LDAP, Active Directory, etc.), your e-mail
server, and enable logging, at a minimum. There are multiple settings pages
available through the Administration UI:

* :doc:`General settings <configuration/general-settings>`
* :doc:`Authentication settings <configuration/authentication-settings>`
* :doc:`Avatar services settings <configuration/avatar-services-settings>`
* :doc:`E-mail settings <configuration/email-settings>`
* :doc:`Diff viewer settings <configuration/diffviewer-settings>`
* :doc:`Logging settings <configuration/logging-settings>`
* :doc:`SSH settings <configuration/ssh-settings>`
* :doc:`File storage settings <configuration/file-storage-settings>`
* :doc:`User Privacy Settings <configuration/privacy-settings>`
* :doc:`Search settings <configuration/search-settings>`

Next, you'll want to configure your repositories, :term:`review groups`, and
:term:`default reviewers`:

* :doc:`Managing repositories <configuration/repositories/index>`

  .. hlist::

     * :ref:`Bazaar <repository-scm-bazaar>`
     * :ref:`Cliosoft SOS <repository-scm-sos>`
     * :ref:`CVS <repository-scm-cvs>`
     * :ref:`Git <repository-scm-git>`
     * :ref:`HCL VersionVault and IBM ClearCase <repository-scm-clearcase>`
     * :ref:`Mercurial <repository-scm-mercurial>`
     * :ref:`Perforce <repository-scm-perforce>`
     * :ref:`Subversion <repository-scm-subversion>`

  .. hlist::

     * :ref:`Assembla <repository-hosting-assembla>`
     * :ref:`AWS CodeCommit <repository-hosting-aws-codecommit>`
     * :ref:`Beanstalk <repository-hosting-beanstalk>`
     * :ref:`Bitbucket <repository-hosting-bitbucket>`
     * :ref:`Bitbucket Server <repository-hosting-bitbucket-server>`
     * :ref:`Codebase <repository-hosting-codebasehq>`
     * :ref:`Fedora Hosted <repository-hosting-fedorahosted>`
     * :ref:`Gerrit <repository-hosting-gerrit>`
     * :ref:`GitHub <repository-hosting-github>`
     * :ref:`GitHub Enterprise <repository-hosting-github-enterprise>`
     * :ref:`GitLab <repository-hosting-gitlab>`
     * :ref:`Gitorious <repository-hosting-gitorious>`
     * :ref:`SourceForge <repository-hosting-sourceforge>`
     * :ref:`Unfuddle STACK <repository-hosting-unfuddle>`
     * :ref:`VisualStudio.com <repository-hosting-visualstudio>`

* :doc:`Managing review groups <configuration/review-groups>`
* :doc:`Managing default reviewers <configuration/default-reviewers>`

You can also configure tighter access control and give special permissions to
users:

* :doc:`Learn about access control <configuration/access-control>`
* :doc:`Manage users and permissions <configuration/users>`
* :doc:`Set up permission groups <configuration/permission-groups>`

That's not all you can set up.

* :doc:`Configure WebHooks <configuration/webhooks>`, which can notify
  in-house or external web services when things happen on Review Board
* :doc:`Manage extensions <extensions/index>`, which can add new features
  to Review Board
* :doc:`Manage Integrations <integrations/index>`, which can add integrations
  between Review Board and third-party services, like:

  * :doc:`Asana <integrations/asana>`
  * :doc:`CircleCI <integrations/circle-ci>`
  * :doc:`Discord <integrations/discord>`
  * :doc:`I Done This <integrations/idonethis>`
  * :ref:`Jenkins CI <integrations-jenkins-ci>`
  * :ref:`Matrix <integrations-matrix>`
  * :doc:`Mattermost <integrations/mattermost>`
  * :ref:`Microsoft Teams <integrations-microsoft-teams>`
  * :doc:`Slack <integrations/slack>`
  * :doc:`Travis CI <integrations/travis-ci>`
  * :doc:`Trello <integrations/trello>`


Site Maintenance
================

Review Board ships with some command line management tools for working with
Review Board site directories, search indexes, handle password resets, and
more.

* :doc:`Using the rb-site tool <sites/rb-site>`
* :doc:`Advanced management command line tools <sites/management-commands>`


.. toctree::
   :maxdepth: 2
   :hidden:

   installation/index
   upgrading/index
   optimization/index
   admin-ui/index
   configuration/index
   extensions/index
   integrations/index
   sites/index
   monitoring/index
