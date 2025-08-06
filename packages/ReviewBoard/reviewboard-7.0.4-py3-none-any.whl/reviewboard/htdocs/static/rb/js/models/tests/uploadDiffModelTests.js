"use strict";

suite('rb/models/uploadDiffModel', function () {
  let reviewRequest;
  let updateDiffView;
  beforeEach(function () {
    reviewRequest = new RB.ReviewRequest({
      id: 123
    });
    updateDiffView = new RB.UpdateDiffView({
      model: new RB.UploadDiffModel({
        changeNumber: reviewRequest.get('commitID'),
        repository: reviewRequest.get('repository'),
        reviewRequest: reviewRequest
      }),
      el: $('#scratch')
    });
  });
  describe('Updating Review Requests', function () {
    it('"Start Over" doesn\'t change reviewRequest attribute', function () {
      spyOn(updateDiffView.model, 'startOver').and.callThrough();
      updateDiffView.model.startOver();
      expect(updateDiffView.model.attributes.reviewRequest).toBe(reviewRequest);
    });
  });
});

//# sourceMappingURL=uploadDiffModelTests.js.map