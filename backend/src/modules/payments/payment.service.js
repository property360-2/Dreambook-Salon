import crypto from 'node:crypto';

import { prisma } from '../../lib/prisma.js';
import { logger } from '../../config/logger.js';

const PAYMENT_INCLUDE = {
  appointment: {
    include: {
      service: true,
      customer: {
        select: {
          id: true,
          name: true,
          email: true,
        },
      },
    },
  },
};

function toPaymentResource(record) {
  return {
    id: record.id,
    status: record.status,
    method: record.method,
    amountCents: record.amountCents,
    transactionId: record.transactionId ?? null,
    appointment: record.appointment
      ? {
          id: record.appointment.id,
          status: record.appointment.status,
          scheduledStart: record.appointment.scheduledStart,
          scheduledEnd: record.appointment.scheduledEnd,
          service: record.appointment.service
            ? {
                id: record.appointment.service.id,
                name: record.appointment.service.name,
                priceCents: record.appointment.service.priceCents,
              }
            : null,
          customer: record.appointment.customer
            ? {
                id: record.appointment.customer.id,
                name: record.appointment.customer.name,
                email: record.appointment.customer.email,
              }
            : null,
        }
      : null,
  };
}

export async function getPayment(id) {
  const payment = await prisma.payment.findUnique({
    where: { id },
    include: PAYMENT_INCLUDE,
  });

  if (!payment) {
    const error = new Error('Payment not found');
    error.status = 404;
    throw error;
  }

  return toPaymentResource(payment);
}

function generateTransactionId() {
  return `TXN-${crypto.randomBytes(5).toString('hex').toUpperCase()}`;
}

export async function createDemoPayment(payload, actor) {
  if (payload.method === 'ONSITE') {
    const error = new Error('Demo payments must use a demo method');
    error.status = 400;
    throw error;
  }

  const result = await prisma.$transaction(async (tx) => {
    const appointment = await tx.appointment.findUnique({
      where: { id: payload.appointmentId },
      include: {
        service: true,
        payment: true,
      },
    });

    if (!appointment) {
      const error = new Error('Appointment not found');
      error.status = 404;
      throw error;
    }

    if (appointment.payment) {
      const error = new Error('Payment already exists for this appointment');
      error.status = 409;
      throw error;
    }

    if (appointment.status === 'CANCELLED') {
      const error = new Error('Cannot initiate payment for a cancelled appointment');
      error.status = 400;
      throw error;
    }

    const payment = await tx.payment.create({
      data: {
        appointmentId: appointment.id,
        method: payload.method,
        amountCents: appointment.service?.priceCents ?? 0,
        status: 'PENDING',
      },
      include: PAYMENT_INCLUDE,
    });

    await tx.appointmentEvent.create({
      data: {
        appointmentId: appointment.id,
        status: 'PAYMENT_PENDING',
        notes: `Demo payment initiated via ${payload.method}`,
        createdById: actor?.id ?? appointment.customerId ?? null,
      },
    });

    return payment;
  });

  logger.info(
    {
      paymentId: result.id,
      appointmentId: result.appointment?.id,
      method: result.method,
    },
    'Demo payment created',
  );

  return toPaymentResource(result);
}

export async function updateDemoPayment(id, payload, actor) {
  const result = await prisma.$transaction(async (tx) => {
    const payment = await tx.payment.findUnique({
      where: { id },
      include: {
        appointment: {
          include: {
            service: true,
            customer: {
              select: {
                id: true,
                name: true,
                email: true,
              },
            },
          },
        },
      },
    });

    if (!payment) {
      const error = new Error('Payment not found');
      error.status = 404;
      throw error;
    }

    if (payment.status !== 'PENDING') {
      const error = new Error('Only pending payments can be updated');
      error.status = 400;
      throw error;
    }

    let transactionId = payment.transactionId;
    let appointmentStatusUpdate = null;
    let eventStatus = 'PAYMENT_UPDATED';

    switch (payload.status) {
      case 'PAID':
        eventStatus = 'PAYMENT_CONFIRMED';
        if (!transactionId) {
          transactionId = generateTransactionId();
        }
        if (!['COMPLETED', 'CANCELLED'].includes(payment.appointment.status)) {
          appointmentStatusUpdate = 'CONFIRMED';
        }
        break;
      case 'FAILED':
        eventStatus = 'PAYMENT_FAILED';
        break;
      case 'CANCELLED':
        eventStatus = 'PAYMENT_CANCELLED';
        break;
      default:
        break;
    }

    await tx.payment.update({
      where: { id },
      data: {
        status: payload.status,
        transactionId,
      },
    });

    if (appointmentStatusUpdate) {
      await tx.appointment.update({
        where: { id: payment.appointmentId },
        data: {
          status: appointmentStatusUpdate,
        },
      });
    }

    await tx.appointmentEvent.create({
      data: {
        appointmentId: payment.appointmentId,
        status: eventStatus,
        notes: `Payment marked as ${payload.status}`,
        createdById: actor?.id ?? null,
      },
    });

    const refreshed = await tx.payment.findUnique({
      where: { id },
      include: PAYMENT_INCLUDE,
    });

    return refreshed;
  });

  logger.info(
    {
      paymentId: result.id,
      status: result.status,
      transactionId: result.transactionId,
    },
    'Demo payment updated',
  );

  return toPaymentResource(result);
}
