import { afterEach, beforeEach, describe, expect, test, jest } from '@jest/globals';

const mockTransaction = jest.fn();
const mockAppointmentFindUnique = jest.fn();
const mockPaymentCreate = jest.fn();
const mockAppointmentEventCreate = jest.fn();
const mockLoggerInfo = jest.fn();

jest.unstable_mockModule('../../config/logger.js', () => ({
  logger: {
    info: mockLoggerInfo,
  },
}));

jest.unstable_mockModule('../../lib/prisma.js', () => ({
  prisma: {
    $transaction: mockTransaction,
  },
}));

const { createDemoPayment } = await import('./payment.service.js');

const mockTx = {
  appointment: {
    findUnique: mockAppointmentFindUnique,
  },
  payment: {
    create: mockPaymentCreate,
  },
  appointmentEvent: {
    create: mockAppointmentEventCreate,
  },
};

beforeEach(() => {
  jest.resetAllMocks();
  mockTransaction.mockImplementation((fn) => fn(mockTx));
});

afterEach(() => {
  jest.clearAllMocks();
});

describe('payment.service createDemoPayment', () => {
  test('creates a payment when appointment exists and has no payment', async () => {
    const appointmentRecord = {
      id: 'appt_1',
      status: 'PENDING',
      customerId: 'user_1',
      payment: null,
      service: {
        priceCents: 4500,
      },
    };

    const createdPayment = {
      id: 'pay_1',
      method: 'DEMO_GCASH',
      status: 'PENDING',
      amountCents: 4500,
      transactionId: null,
      appointment: {
        id: 'appt_1',
        status: 'PENDING',
        scheduledStart: new Date(),
        scheduledEnd: new Date(),
        service: {
          id: 'svc_1',
          name: 'Signature Haircut',
          priceCents: 4500,
        },
        customer: {
          id: 'user_1',
          name: 'Sample Customer',
          email: 'customer@example.test',
        },
      },
    };

    mockAppointmentFindUnique.mockResolvedValueOnce(appointmentRecord);
    mockPaymentCreate.mockResolvedValueOnce(createdPayment);

    const payment = await createDemoPayment(
      { appointmentId: 'appt_1', method: 'DEMO_GCASH' },
      { id: 'user_admin' },
    );

    expect(mockAppointmentFindUnique).toHaveBeenCalledWith({
      where: { id: 'appt_1' },
      include: expect.any(Object),
    });
    expect(mockPaymentCreate).toHaveBeenCalledWith({
      data: expect.objectContaining({
        appointmentId: 'appt_1',
        method: 'DEMO_GCASH',
        amountCents: 4500,
      }),
      include: expect.any(Object),
    });
    expect(payment).toMatchObject({
      id: 'pay_1',
      status: 'PENDING',
      appointment: expect.objectContaining({ id: 'appt_1' }),
    });
    expect(mockLoggerInfo).toHaveBeenCalled();
  });

  test('throws when a payment already exists for the appointment', async () => {
    mockAppointmentFindUnique.mockResolvedValueOnce({
      id: 'appt_1',
      payment: { id: 'pay_existing' },
      service: { priceCents: 2000 },
    });

    await expect(
      createDemoPayment({ appointmentId: 'appt_1', method: 'DEMO_GCASH' }),
    ).rejects.toMatchObject({ status: 409 });

    expect(mockPaymentCreate).not.toHaveBeenCalled();
  });
});
