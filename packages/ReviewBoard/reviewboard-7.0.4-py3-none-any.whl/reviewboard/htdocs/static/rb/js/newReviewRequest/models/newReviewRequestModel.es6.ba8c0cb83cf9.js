/**
 * Model data for :js:class:`RB.NewReviewRequestView`.
 *
 * Model Attributes:
 *     repositories (Backbone.Collection of RB.Repository):
 *         The active repositories which can be selected.
 */
RB.NewReviewRequest = RB.Page.extend({
    defaults() {
        return _.defaults({
            repositories: null,
        }, _.result(RB.Page.prototype.defaults));
    },

    /**
     * Parse the data needed for the New Review Request page.
     *
     * Args:
     *     rsp (Array):
     *         The data provided to the page from the server.
     *
     * Returns:
     *     object:
     *     The parsed data used to populate the attributes.
     */
    parse(rsp) {
        return _.extend(RB.Page.prototype.parse.call(this, rsp), {
            repositories: new RB.RepositoryCollection(null, {
                repositories: rsp.repositories.map(
                    repository => new RB.Repository(repository)),
                localSitePrefix: rsp.localSitePrefix,
            }),
        });
    },
});
