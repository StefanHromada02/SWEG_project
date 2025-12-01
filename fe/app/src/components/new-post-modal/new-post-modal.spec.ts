import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NewPostModal } from './new-post-modal';

describe('NewPostModal', () => {
  let component: NewPostModal;
  let fixture: ComponentFixture<NewPostModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NewPostModal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NewPostModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
