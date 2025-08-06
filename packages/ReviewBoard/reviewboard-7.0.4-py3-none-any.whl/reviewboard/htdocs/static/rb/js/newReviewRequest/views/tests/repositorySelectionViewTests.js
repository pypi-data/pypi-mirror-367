"use strict";

suite('rb/newReviewRequest/views/RepositorySelectionView', function () {
  let collection;
  let view;
  beforeEach(function () {
    collection = new Backbone.Collection([{
      name: 'Bitbucket Test'
    }, {
      name: 'GitHub Test'
    }, {
      name: 'GitLab Test'
    }, {
      name: 'Local Git Test'
    }], {
      model: RB.Repository
    });
    view = new RB.RepositorySelectionView({
      collection: collection
    });
  });
  describe('Rendering', function () {
    it('With items', function () {
      view.render();
      const children = view.$el.find('.repository');
      expect(children.length).toBe(collection.models.length);
      for (let i = 0; i < children.length; i++) {
        const name = collection.models[i].get('name');
        expect($(children[i]).text().trim()).toBe(name);
      }
    });
  });
  describe('Selected event', function () {
    it('When clicked', function () {
      let handlerCalled = false;
      view.render();
      view.on('selected', repository => {
        expect(repository.get('name')).toBe('GitHub Test');
        handlerCalled = true;
      });
      const children = view.$el.find('.repository');
      $(children[1]).click();
      expect(handlerCalled).toBe(true);
    });
  });
});

//# sourceMappingURL=repositorySelectionViewTests.js.map