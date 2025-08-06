suite('rb/newReviewRequest/views/PostCommitView', function() {
    let repository;
    let commits;
    let model;
    let view;

    beforeEach(function() {
        repository = new RB.Repository({
            name: 'Repo',
            supportsPostCommit: true,
        });

        spyOn(repository.branches, 'sync').and.callFake(
            (method, collection, options) => {
                options.success({
                    stat: 'ok',
                    branches: [
                        {
                            name: 'master',
                            commit: '859d4e148ce3ce60bbda6622cdbe5c2c2f8d9817',
                            'default': true,
                        },
                        {
                            name: 'release-1.7.x',
                            commit: '92463764015ef463b4b6d1a1825fee7aeec8cb15',
                            'default': false,
                        },
                        {
                            name: 'release-1.6.x',
                            commit: 'a15d0e635064a2e1929ce1bf3bc8d4aa65738b64',
                            'default': false,
                        },
                    ],
                });
            }
        );

        spyOn(repository, 'getCommits').and.callFake(options => {
            commits = new RB.RepositoryCommits([], {
                urlBase: _.result(this, 'url') + 'commits/',
                start: options.start,
                branch: options.branch,
            });

            spyOn(commits, 'sync').and.callFake(
                (method, collection, options) => {
                    options.success({
                        stat: 'ok',
                        commits: [
                            {
                                authorName: 'Author 1',
                                date: '2013-07-22T03:51:50Z',
                                id: '3',
                                message: 'Summary 1\n\nMessage 1',
                                parent: '2',
                            },
                            {
                                authorName: 'Author 2',
                                date: '2013-07-22T03:50:46Z',
                                id: '2',
                                message: 'Summary 2\n\nMessage 2',
                                parent: '1',
                            },
                            {
                                authorName: 'Author 3',
                                date: '2013-07-21T08:05:45Z',
                                id: '1',
                                message: 'Summary 3\n\nMessage 3',
                                parent: '',
                            },
                        ],
                    });
                }
            );

            return commits;
        });

        model = new RB.PostCommitModel({ repository: repository });
        view = new RB.PostCommitView({
            model: model,
            $scrollContainer: $('<div>'),
        });

        spyOn(RB.PostCommitView.prototype, '_onCreateReviewRequest')
            .and.callThrough();

        expect(repository.branches.sync).toHaveBeenCalled();
    });

    it('Render', function() {
        view.render();

        expect(commits.sync).toHaveBeenCalled();

        expect(view._branchesView.$el.children().length).toBe(3);
        expect(view._commitsView.$el.children().length).toBe(3);
    });

    it('Create', function(done) {
        view.render();

        let commit;

        spyOn(RB.ReviewRequest.prototype, 'save').and.resolveTo();
        spyOn(RB, 'navigateTo').and.callFake(() => {
            expect(RB.PostCommitView.prototype._onCreateReviewRequest)
                .toHaveBeenCalled();
            expect(RB.ReviewRequest.prototype.save).toHaveBeenCalled();

            expect(RB.ReviewRequest.prototype.save.calls.count()).toBe(1);

            const call = RB.ReviewRequest.prototype.save.calls.mostRecent();
            expect(call.object.get('commitID')).toBe(commit.get('id'));

            done();
        });

        commit = commits.models[1];
        commit.trigger('create', commit);
    });

    describe('Error handling', function() {
        describe('Branches', function() {
            const errorText = 'Oh no';
            let returnError;

            beforeEach(async function() {
                spyOn(repository.branches, 'fetch').and.callFake(
                    () => returnError
                        ? Promise.reject(
                            new BackboneError(model, { errorText }, {}))
                        : Promise.resolve());

                returnError = true;

                spyOn(RB.PostCommitView.prototype, '_showLoadError')
                    .and.callThrough();

                await view._loadBranches();
            });

            it('UI state', function() {
                expect(repository.branches.fetch).toHaveBeenCalled();

                expect(view._showLoadError).toHaveBeenCalled();
                expect(view._showLoadError.calls.argsFor(0)[1]).toBe(errorText);

                expect(view._branchesView.$el.css('display')).toBe('none');
                expect(view._errorView).toBeTruthy();
                expect(view._commitsView).toBeFalsy();
                expect(view._errorView.$el.find('.error-text').text().trim())
                    .toBe('Oh no');
            });

            it('Reloading', function(done) {
                spyOn(view, '_onReloadBranchesClicked').and.callFake(() => {
                    view._loadBranches().finally(() => {
                        expect(view._errorView).toBe(null);
                        expect(view._branchesView.$el.css('display'))
                            .not.toBe('none');

                        done();
                    });
                });

                /* Make sure the spy is called from the event handler. */
                view.delegateEvents();

                returnError = false;

                expect(view._errorView).toBeTruthy();
                const $reload = view._errorView.$el.find('.ink-c-button');
                expect($reload.length).toBe(1);
                $reload.click();
            });
        });

        describe('Commits', function() {
            const errorText = 'Oh no';
            let returnError;

            beforeEach(async function() {
                view.render();

                spyOn(RB.RepositoryCommits.prototype, 'fetch').and.callFake(
                    () => returnError
                        ? Promise.reject(
                            new BackboneError(model, { errorText }, {}))
                        : Promise.resolve());

                returnError = true;

                spyOn(RB.PostCommitView.prototype, '_showLoadError')
                    .and.callThrough();

                await view._loadCommits();
            });

            it('UI state', function() {
                expect(view._commitsCollection.fetch).toHaveBeenCalled();

                expect(view._showLoadError).toHaveBeenCalled();
                expect(view._showLoadError.calls.argsFor(0)[1]).toBe(errorText);

                expect(view._commitsView.$el.css('display')).toBe('none');
                expect(view._errorView).toBeTruthy();
                expect(view._commitsView).toBeTruthy();
                expect(view._commitsView.$el.css('display')).toBe('none');
                expect(view._errorView.$el.find('.error-text').text().trim())
                    .toBe('Oh no');
            });

            it('Reloading', function(done) {
                spyOn(view, '_onReloadCommitsClicked').and.callFake(() => {
                    view._loadCommits().finally(() => {
                        expect(view._errorView).toBe(null);

                        /*
                         * Chrome returns an empty string, while Firefox
                         * returns "block".
                         */
                        const display = view._commitsView.$el.css('display');
                        expect(display === 'block' || display === '')
                            .toBe(true);

                        done();
                    });
                });

                /* Make sure the spy is called from the event handler. */
                view.delegateEvents();

                returnError = false;

                expect(view._errorView).toBeTruthy();
                const $reload = view._errorView.$el.find('.ink-c-button');
                expect($reload.length).toBe(1);
                $reload.click();
            });
        });
    });
});
