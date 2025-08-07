#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* fe.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscfe.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesettype_ PETSCFESETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesettype_ petscfesettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegettype_ PETSCFEGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegettype_ petscfegettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfeviewfromoptions_ PETSCFEVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfeviewfromoptions_ petscfeviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfeview_ PETSCFEVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfeview_ petscfeview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesetfromoptions_ PETSCFESETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesetfromoptions_ petscfesetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesetup_ PETSCFESETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesetup_ petscfesetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfedestroy_ PETSCFEDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfedestroy_ petscfedestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfecreate_ PETSCFECREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfecreate_ petscfecreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegetspatialdimension_ PETSCFEGETSPATIALDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegetspatialdimension_ petscfegetspatialdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesetnumcomponents_ PETSCFESETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesetnumcomponents_ petscfesetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegetnumcomponents_ PETSCFEGETNUMCOMPONENTS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegetnumcomponents_ petscfegetnumcomponents
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesettilesizes_ PETSCFESETTILESIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesettilesizes_ petscfesettilesizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegettilesizes_ PETSCFEGETTILESIZES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegettilesizes_ petscfegettilesizes
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegetbasisspace_ PETSCFEGETBASISSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegetbasisspace_ petscfegetbasisspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesetbasisspace_ PETSCFESETBASISSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesetbasisspace_ petscfesetbasisspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegetdualspace_ PETSCFEGETDUALSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegetdualspace_ petscfegetdualspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesetdualspace_ PETSCFESETDUALSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesetdualspace_ petscfesetdualspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegetquadrature_ PETSCFEGETQUADRATURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegetquadrature_ petscfegetquadrature
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesetquadrature_ PETSCFESETQUADRATURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesetquadrature_ petscfesetquadrature
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegetfacequadrature_ PETSCFEGETFACEQUADRATURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegetfacequadrature_ petscfegetfacequadrature
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesetfacequadrature_ PETSCFESETFACEQUADRATURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesetfacequadrature_ petscfesetfacequadrature
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfecopyquadrature_ PETSCFECOPYQUADRATURE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfecopyquadrature_ petscfecopyquadrature
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petsctabulationdestroy_ PETSCTABULATIONDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petsctabulationdestroy_ petsctabulationdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegetdimension_ PETSCFEGETDIMENSION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegetdimension_ petscfegetdimension
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfepushforward_ PETSCFEPUSHFORWARD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfepushforward_ petscfepushforward
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfepushforwardgradient_ PETSCFEPUSHFORWARDGRADIENT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfepushforwardgradient_ petscfepushforwardgradient
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfepushforwardhessian_ PETSCFEPUSHFORWARDHESSIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfepushforwardhessian_ petscfepushforwardhessian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfeintegrate_ PETSCFEINTEGRATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfeintegrate_ petscfeintegrate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfeintegrateresidual_ PETSCFEINTEGRATERESIDUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfeintegrateresidual_ petscfeintegrateresidual
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfeintegratebdresidual_ PETSCFEINTEGRATEBDRESIDUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfeintegratebdresidual_ petscfeintegratebdresidual
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfeintegratehybridresidual_ PETSCFEINTEGRATEHYBRIDRESIDUAL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfeintegratehybridresidual_ petscfeintegratehybridresidual
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfeintegratejacobian_ PETSCFEINTEGRATEJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfeintegratejacobian_ petscfeintegratejacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfeintegratebdjacobian_ PETSCFEINTEGRATEBDJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfeintegratebdjacobian_ petscfeintegratebdjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfeintegratehybridjacobian_ PETSCFEINTEGRATEHYBRIDJACOBIAN
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfeintegratehybridjacobian_ petscfeintegratehybridjacobian
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfegetheightsubspace_ PETSCFEGETHEIGHTSUBSPACE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfegetheightsubspace_ petscfegetheightsubspace
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscferefine_ PETSCFEREFINE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscferefine_ petscferefine
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfecreatefromspaces_ PETSCFECREATEFROMSPACES
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfecreatefromspaces_ petscfecreatefromspaces
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfecreatedefault_ PETSCFECREATEDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfecreatedefault_ petscfecreatedefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfecreatebycell_ PETSCFECREATEBYCELL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfecreatebycell_ petscfecreatebycell
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfecreatelagrange_ PETSCFECREATELAGRANGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfecreatelagrange_ petscfecreatelagrange
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfecreatelagrangebycell_ PETSCFECREATELAGRANGEBYCELL
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfecreatelagrangebycell_ petscfecreatelagrangebycell
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfelimitdegree_ PETSCFELIMITDEGREE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfelimitdegree_ petscfelimitdegree
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscfesetname_ PETSCFESETNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscfesetname_ petscfesetname
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscfesettype_(PetscFE fem,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(fem);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscFESetType(
	(PetscFE)PetscToPointer((fem) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscfegettype_(PetscFE fem,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFEGetType(
	(PetscFE)PetscToPointer((fem) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petscfeviewfromoptions_(PetscFE A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscFEViewFromOptions(
	(PetscFE)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscfeview_(PetscFE fem,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
CHKFORTRANNULLOBJECT(viewer);
*ierr = PetscFEView(
	(PetscFE)PetscToPointer((fem) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  petscfesetfromoptions_(PetscFE fem, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFESetFromOptions(
	(PetscFE)PetscToPointer((fem) ));
}
PETSC_EXTERN void  petscfesetup_(PetscFE fem, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFESetUp(
	(PetscFE)PetscToPointer((fem) ));
}
PETSC_EXTERN void  petscfedestroy_(PetscFE *fem, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(fem);
 PetscBool fem_null = !*(void**) fem ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFEDestroy(fem);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fem_null && !*(void**) fem) * (void **) fem = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(fem);
 }
PETSC_EXTERN void  petscfecreate_(MPI_Fint * comm,PetscFE *fem, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(fem);
 PetscBool fem_null = !*(void**) fem ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFECreate(
	MPI_Comm_f2c(*(comm)),fem);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fem_null && !*(void**) fem) * (void **) fem = (void *)-2;
}
PETSC_EXTERN void  petscfegetspatialdimension_(PetscFE fem,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
CHKFORTRANNULLINTEGER(dim);
*ierr = PetscFEGetSpatialDimension(
	(PetscFE)PetscToPointer((fem) ),dim);
}
PETSC_EXTERN void  petscfesetnumcomponents_(PetscFE fem,PetscInt *comp, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFESetNumComponents(
	(PetscFE)PetscToPointer((fem) ),*comp);
}
PETSC_EXTERN void  petscfegetnumcomponents_(PetscFE fem,PetscInt *comp, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
CHKFORTRANNULLINTEGER(comp);
*ierr = PetscFEGetNumComponents(
	(PetscFE)PetscToPointer((fem) ),comp);
}
PETSC_EXTERN void  petscfesettilesizes_(PetscFE fem,PetscInt *blockSize,PetscInt *numBlocks,PetscInt *batchSize,PetscInt *numBatches, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFESetTileSizes(
	(PetscFE)PetscToPointer((fem) ),*blockSize,*numBlocks,*batchSize,*numBatches);
}
PETSC_EXTERN void  petscfegettilesizes_(PetscFE fem,PetscInt *blockSize,PetscInt *numBlocks,PetscInt *batchSize,PetscInt *numBatches, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
CHKFORTRANNULLINTEGER(blockSize);
CHKFORTRANNULLINTEGER(numBlocks);
CHKFORTRANNULLINTEGER(batchSize);
CHKFORTRANNULLINTEGER(numBatches);
*ierr = PetscFEGetTileSizes(
	(PetscFE)PetscToPointer((fem) ),blockSize,numBlocks,batchSize,numBatches);
}
PETSC_EXTERN void  petscfegetbasisspace_(PetscFE fem,PetscSpace *sp, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscFEGetBasisSpace(
	(PetscFE)PetscToPointer((fem) ),sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
}
PETSC_EXTERN void  petscfesetbasisspace_(PetscFE fem,PetscSpace sp, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscFESetBasisSpace(
	(PetscFE)PetscToPointer((fem) ),
	(PetscSpace)PetscToPointer((sp) ));
}
PETSC_EXTERN void  petscfegetdualspace_(PetscFE fem,PetscDualSpace *sp, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
PetscBool sp_null = !*(void**) sp ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscFEGetDualSpace(
	(PetscFE)PetscToPointer((fem) ),sp);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sp_null && !*(void**) sp) * (void **) sp = (void *)-2;
}
PETSC_EXTERN void  petscfesetdualspace_(PetscFE fem,PetscDualSpace sp, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
CHKFORTRANNULLOBJECT(sp);
*ierr = PetscFESetDualSpace(
	(PetscFE)PetscToPointer((fem) ),
	(PetscDualSpace)PetscToPointer((sp) ));
}
PETSC_EXTERN void  petscfegetquadrature_(PetscFE fem,PetscQuadrature *q, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
PetscBool q_null = !*(void**) q ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(q);
*ierr = PetscFEGetQuadrature(
	(PetscFE)PetscToPointer((fem) ),q);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! q_null && !*(void**) q) * (void **) q = (void *)-2;
}
PETSC_EXTERN void  petscfesetquadrature_(PetscFE fem,PetscQuadrature q, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
CHKFORTRANNULLOBJECT(q);
*ierr = PetscFESetQuadrature(
	(PetscFE)PetscToPointer((fem) ),
	(PetscQuadrature)PetscToPointer((q) ));
}
PETSC_EXTERN void  petscfegetfacequadrature_(PetscFE fem,PetscQuadrature *q, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
PetscBool q_null = !*(void**) q ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(q);
*ierr = PetscFEGetFaceQuadrature(
	(PetscFE)PetscToPointer((fem) ),q);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! q_null && !*(void**) q) * (void **) q = (void *)-2;
}
PETSC_EXTERN void  petscfesetfacequadrature_(PetscFE fem,PetscQuadrature q, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
CHKFORTRANNULLOBJECT(q);
*ierr = PetscFESetFaceQuadrature(
	(PetscFE)PetscToPointer((fem) ),
	(PetscQuadrature)PetscToPointer((q) ));
}
PETSC_EXTERN void  petscfecopyquadrature_(PetscFE sfe,PetscFE tfe, int *ierr)
{
CHKFORTRANNULLOBJECT(sfe);
CHKFORTRANNULLOBJECT(tfe);
*ierr = PetscFECopyQuadrature(
	(PetscFE)PetscToPointer((sfe) ),
	(PetscFE)PetscToPointer((tfe) ));
}
PETSC_EXTERN void  petsctabulationdestroy_(PetscTabulation *T, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(T);
 PetscBool T_null = !*(void**) T ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(T);
*ierr = PetscTabulationDestroy(T);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! T_null && !*(void**) T) * (void **) T = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(T);
 }
PETSC_EXTERN void  petscfegetdimension_(PetscFE fem,PetscInt *dim, int *ierr)
{
CHKFORTRANNULLOBJECT(fem);
CHKFORTRANNULLINTEGER(dim);
*ierr = PetscFEGetDimension(
	(PetscFE)PetscToPointer((fem) ),dim);
}
PETSC_EXTERN void  petscfepushforward_(PetscFE fe,PetscFEGeom *fegeom,PetscInt *Nv,PetscScalar vals[], int *ierr)
{
CHKFORTRANNULLOBJECT(fe);
CHKFORTRANNULLSCALAR(vals);
*ierr = PetscFEPushforward(
	(PetscFE)PetscToPointer((fe) ),
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nv,vals);
}
PETSC_EXTERN void  petscfepushforwardgradient_(PetscFE fe,PetscFEGeom *fegeom,PetscInt *Nv,PetscScalar vals[], int *ierr)
{
CHKFORTRANNULLOBJECT(fe);
CHKFORTRANNULLSCALAR(vals);
*ierr = PetscFEPushforwardGradient(
	(PetscFE)PetscToPointer((fe) ),
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nv,vals);
}
PETSC_EXTERN void  petscfepushforwardhessian_(PetscFE fe,PetscFEGeom *fegeom,PetscInt *Nv,PetscScalar vals[], int *ierr)
{
CHKFORTRANNULLOBJECT(fe);
CHKFORTRANNULLSCALAR(vals);
*ierr = PetscFEPushforwardHessian(
	(PetscFE)PetscToPointer((fe) ),
	(PetscFEGeom* )PetscToPointer((fegeom) ),*Nv,vals);
}
PETSC_EXTERN void  petscfeintegrate_(PetscDS prob,PetscInt *field,PetscInt *Ne,PetscFEGeom *cgeom, PetscScalar coefficients[],PetscDS probAux, PetscScalar coefficientsAux[],PetscScalar integral[], int *ierr)
{
CHKFORTRANNULLOBJECT(prob);
CHKFORTRANNULLSCALAR(coefficients);
CHKFORTRANNULLOBJECT(probAux);
CHKFORTRANNULLSCALAR(coefficientsAux);
CHKFORTRANNULLSCALAR(integral);
*ierr = PetscFEIntegrate(
	(PetscDS)PetscToPointer((prob) ),*field,*Ne,
	(PetscFEGeom* )PetscToPointer((cgeom) ),coefficients,
	(PetscDS)PetscToPointer((probAux) ),coefficientsAux,integral);
}
PETSC_EXTERN void  petscfeintegrateresidual_(PetscDS ds,PetscFormKey *key,PetscInt *Ne,PetscFEGeom *cgeom, PetscScalar coefficients[], PetscScalar coefficients_t[],PetscDS probAux, PetscScalar coefficientsAux[],PetscReal *t,PetscScalar elemVec[], int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLSCALAR(coefficients);
CHKFORTRANNULLSCALAR(coefficients_t);
CHKFORTRANNULLOBJECT(probAux);
CHKFORTRANNULLSCALAR(coefficientsAux);
CHKFORTRANNULLSCALAR(elemVec);
*ierr = PetscFEIntegrateResidual(
	(PetscDS)PetscToPointer((ds) ),*key,*Ne,
	(PetscFEGeom* )PetscToPointer((cgeom) ),coefficients,coefficients_t,
	(PetscDS)PetscToPointer((probAux) ),coefficientsAux,*t,elemVec);
}
PETSC_EXTERN void  petscfeintegratebdresidual_(PetscDS ds,PetscWeakForm wf,PetscFormKey *key,PetscInt *Ne,PetscFEGeom *fgeom, PetscScalar coefficients[], PetscScalar coefficients_t[],PetscDS probAux, PetscScalar coefficientsAux[],PetscReal *t,PetscScalar elemVec[], int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLOBJECT(wf);
CHKFORTRANNULLSCALAR(coefficients);
CHKFORTRANNULLSCALAR(coefficients_t);
CHKFORTRANNULLOBJECT(probAux);
CHKFORTRANNULLSCALAR(coefficientsAux);
CHKFORTRANNULLSCALAR(elemVec);
*ierr = PetscFEIntegrateBdResidual(
	(PetscDS)PetscToPointer((ds) ),
	(PetscWeakForm)PetscToPointer((wf) ),*key,*Ne,
	(PetscFEGeom* )PetscToPointer((fgeom) ),coefficients,coefficients_t,
	(PetscDS)PetscToPointer((probAux) ),coefficientsAux,*t,elemVec);
}
PETSC_EXTERN void  petscfeintegratehybridresidual_(PetscDS ds,PetscDS dsIn,PetscFormKey *key,PetscInt *s,PetscInt *Ne,PetscFEGeom *fgeom, PetscScalar coefficients[], PetscScalar coefficients_t[],PetscDS probAux, PetscScalar coefficientsAux[],PetscReal *t,PetscScalar elemVec[], int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLOBJECT(dsIn);
CHKFORTRANNULLSCALAR(coefficients);
CHKFORTRANNULLSCALAR(coefficients_t);
CHKFORTRANNULLOBJECT(probAux);
CHKFORTRANNULLSCALAR(coefficientsAux);
CHKFORTRANNULLSCALAR(elemVec);
*ierr = PetscFEIntegrateHybridResidual(
	(PetscDS)PetscToPointer((ds) ),
	(PetscDS)PetscToPointer((dsIn) ),*key,*s,*Ne,
	(PetscFEGeom* )PetscToPointer((fgeom) ),coefficients,coefficients_t,
	(PetscDS)PetscToPointer((probAux) ),coefficientsAux,*t,elemVec);
}
PETSC_EXTERN void  petscfeintegratejacobian_(PetscDS ds,PetscFEJacobianType *jtype,PetscFormKey *key,PetscInt *Ne,PetscFEGeom *cgeom, PetscScalar coefficients[], PetscScalar coefficients_t[],PetscDS probAux, PetscScalar coefficientsAux[],PetscReal *t,PetscReal *u_tshift,PetscScalar elemMat[], int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLSCALAR(coefficients);
CHKFORTRANNULLSCALAR(coefficients_t);
CHKFORTRANNULLOBJECT(probAux);
CHKFORTRANNULLSCALAR(coefficientsAux);
CHKFORTRANNULLSCALAR(elemMat);
*ierr = PetscFEIntegrateJacobian(
	(PetscDS)PetscToPointer((ds) ),*jtype,*key,*Ne,
	(PetscFEGeom* )PetscToPointer((cgeom) ),coefficients,coefficients_t,
	(PetscDS)PetscToPointer((probAux) ),coefficientsAux,*t,*u_tshift,elemMat);
}
PETSC_EXTERN void  petscfeintegratebdjacobian_(PetscDS ds,PetscWeakForm wf,PetscFEJacobianType *jtype,PetscFormKey *key,PetscInt *Ne,PetscFEGeom *fgeom, PetscScalar coefficients[], PetscScalar coefficients_t[],PetscDS probAux, PetscScalar coefficientsAux[],PetscReal *t,PetscReal *u_tshift,PetscScalar elemMat[], int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLOBJECT(wf);
CHKFORTRANNULLSCALAR(coefficients);
CHKFORTRANNULLSCALAR(coefficients_t);
CHKFORTRANNULLOBJECT(probAux);
CHKFORTRANNULLSCALAR(coefficientsAux);
CHKFORTRANNULLSCALAR(elemMat);
*ierr = PetscFEIntegrateBdJacobian(
	(PetscDS)PetscToPointer((ds) ),
	(PetscWeakForm)PetscToPointer((wf) ),*jtype,*key,*Ne,
	(PetscFEGeom* )PetscToPointer((fgeom) ),coefficients,coefficients_t,
	(PetscDS)PetscToPointer((probAux) ),coefficientsAux,*t,*u_tshift,elemMat);
}
PETSC_EXTERN void  petscfeintegratehybridjacobian_(PetscDS ds,PetscDS dsIn,PetscFEJacobianType *jtype,PetscFormKey *key,PetscInt *s,PetscInt *Ne,PetscFEGeom *fgeom, PetscScalar coefficients[], PetscScalar coefficients_t[],PetscDS probAux, PetscScalar coefficientsAux[],PetscReal *t,PetscReal *u_tshift,PetscScalar elemMat[], int *ierr)
{
CHKFORTRANNULLOBJECT(ds);
CHKFORTRANNULLOBJECT(dsIn);
CHKFORTRANNULLSCALAR(coefficients);
CHKFORTRANNULLSCALAR(coefficients_t);
CHKFORTRANNULLOBJECT(probAux);
CHKFORTRANNULLSCALAR(coefficientsAux);
CHKFORTRANNULLSCALAR(elemMat);
*ierr = PetscFEIntegrateHybridJacobian(
	(PetscDS)PetscToPointer((ds) ),
	(PetscDS)PetscToPointer((dsIn) ),*jtype,*key,*s,*Ne,
	(PetscFEGeom* )PetscToPointer((fgeom) ),coefficients,coefficients_t,
	(PetscDS)PetscToPointer((probAux) ),coefficientsAux,*t,*u_tshift,elemMat);
}
PETSC_EXTERN void  petscfegetheightsubspace_(PetscFE fe,PetscInt *height,PetscFE *subfe, int *ierr)
{
CHKFORTRANNULLOBJECT(fe);
PetscBool subfe_null = !*(void**) subfe ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(subfe);
*ierr = PetscFEGetHeightSubspace(
	(PetscFE)PetscToPointer((fe) ),*height,subfe);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! subfe_null && !*(void**) subfe) * (void **) subfe = (void *)-2;
}
PETSC_EXTERN void  petscferefine_(PetscFE fe,PetscFE *feRef, int *ierr)
{
CHKFORTRANNULLOBJECT(fe);
PetscBool feRef_null = !*(void**) feRef ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(feRef);
*ierr = PetscFERefine(
	(PetscFE)PetscToPointer((fe) ),feRef);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! feRef_null && !*(void**) feRef) * (void **) feRef = (void *)-2;
}
PETSC_EXTERN void  petscfecreatefromspaces_(PetscSpace P,PetscDualSpace Q,PetscQuadrature q,PetscQuadrature fq,PetscFE *fem, int *ierr)
{
CHKFORTRANNULLOBJECT(P);
CHKFORTRANNULLOBJECT(Q);
CHKFORTRANNULLOBJECT(q);
CHKFORTRANNULLOBJECT(fq);
PetscBool fem_null = !*(void**) fem ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFECreateFromSpaces(
	(PetscSpace)PetscToPointer((P) ),
	(PetscDualSpace)PetscToPointer((Q) ),
	(PetscQuadrature)PetscToPointer((q) ),
	(PetscQuadrature)PetscToPointer((fq) ),fem);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fem_null && !*(void**) fem) * (void **) fem = (void *)-2;
}
PETSC_EXTERN void  petscfecreatedefault_(MPI_Fint * comm,PetscInt *dim,PetscInt *Nc,PetscBool *isSimplex, char prefix[],PetscInt *qorder,PetscFE *fem, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool fem_null = !*(void**) fem ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fem);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscFECreateDefault(
	MPI_Comm_f2c(*(comm)),*dim,*Nc,*isSimplex,_cltmp0,*qorder,fem);
  FREECHAR(prefix,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fem_null && !*(void**) fem) * (void **) fem = (void *)-2;
}
PETSC_EXTERN void  petscfecreatebycell_(MPI_Fint * comm,PetscInt *dim,PetscInt *Nc,DMPolytopeType *ct, char prefix[],PetscInt *qorder,PetscFE *fem, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
PetscBool fem_null = !*(void**) fem ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fem);
/* insert Fortran-to-C conversion for prefix */
  FIXCHAR(prefix,cl0,_cltmp0);
*ierr = PetscFECreateByCell(
	MPI_Comm_f2c(*(comm)),*dim,*Nc,*ct,_cltmp0,*qorder,fem);
  FREECHAR(prefix,_cltmp0);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fem_null && !*(void**) fem) * (void **) fem = (void *)-2;
}
PETSC_EXTERN void  petscfecreatelagrange_(MPI_Fint * comm,PetscInt *dim,PetscInt *Nc,PetscBool *isSimplex,PetscInt *k,PetscInt *qorder,PetscFE *fem, int *ierr)
{
PetscBool fem_null = !*(void**) fem ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFECreateLagrange(
	MPI_Comm_f2c(*(comm)),*dim,*Nc,*isSimplex,*k,*qorder,fem);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fem_null && !*(void**) fem) * (void **) fem = (void *)-2;
}
PETSC_EXTERN void  petscfecreatelagrangebycell_(MPI_Fint * comm,PetscInt *dim,PetscInt *Nc,DMPolytopeType *ct,PetscInt *k,PetscInt *qorder,PetscFE *fem, int *ierr)
{
PetscBool fem_null = !*(void**) fem ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(fem);
*ierr = PetscFECreateLagrangeByCell(
	MPI_Comm_f2c(*(comm)),*dim,*Nc,*ct,*k,*qorder,fem);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! fem_null && !*(void**) fem) * (void **) fem = (void *)-2;
}
PETSC_EXTERN void  petscfelimitdegree_(PetscFE fe,PetscInt *minDegree,PetscInt *maxDegree,PetscFE *newfe, int *ierr)
{
CHKFORTRANNULLOBJECT(fe);
PetscBool newfe_null = !*(void**) newfe ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newfe);
*ierr = PetscFELimitDegree(
	(PetscFE)PetscToPointer((fe) ),*minDegree,*maxDegree,newfe);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newfe_null && !*(void**) newfe) * (void **) newfe = (void *)-2;
}
PETSC_EXTERN void  petscfesetname_(PetscFE fe, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(fe);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscFESetName(
	(PetscFE)PetscToPointer((fe) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
#if defined(__cplusplus)
}
#endif
